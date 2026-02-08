from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from datetime import datetime

from app.db.mongo import db
from app.schemas.transaction import TransactionCreate
from app.schemas.transaction_entry import TransactionEntryCreate
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", status_code=201)
async def create_transaction(payload: TransactionCreate):
    try:
        # Converte IDs string para ObjectId
        transaction_data = {
            "description": payload.description,
            "amount": payload.amount,
            "flow_type": payload.flow_type.value,
            "transaction_type": payload.transaction_type.value,
            "payment_method": payload.payment_method.model_dump(),
            "date": datetime.combine(payload.date, datetime.min.time()),
            "account_id": ObjectId(payload.account_id) if payload.account_id else None,
            "category_id": ObjectId(payload.category_id) if payload.category_id else None,
            "household_id": ObjectId(payload.household_id) if payload.household_id else None,
        }
        
        if payload.transaction_type == "installment":
            transaction_data["installments"] = payload.installments
            transaction_data["total_amount"] = payload.total_amount

        result = await db.transactions.insert_one(transaction_data)
        transaction_id = result.inserted_id

        # 2. gera lançamentos
        entries = TransactionService.generate_entries(payload)

        # 3. salva lançamentos
        entries_to_insert = []
        for entry in entries:
            entry_dict = entry.model_dump(exclude={"id"})
            entry_dict["transaction_id"] = transaction_id
            # Converter date para datetime para MongoDB
            entry_dict["due_date"] = datetime.combine(entry_dict["due_date"], datetime.min.time())
            entries_to_insert.append(entry_dict)

        if entries_to_insert:
            await db.transaction_entries.insert_many(entries_to_insert)

        return {
            "message": "Transação criada com sucesso",
            "transaction_id": str(transaction_id),
            "entries_created": len(entries_to_insert)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Erro de validação: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar transação: {str(e)}")

@router.get("/", response_model=List[dict])
async def list_transactions(household_id: str):
    cursor = db.transactions.find(
        {"household_id": ObjectId(household_id)}
    )

    transactions = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        transactions.append(doc)

    return transactions

@router.get("/entries/month/{year}/{month}")
async def list_entries_by_month(
    household_id: str,
    year: int,
    month: int
):
    competence = f"{year}-{str(month).zfill(2)}"

    cursor = db.transaction_entries.find({
        "household_id": ObjectId(household_id),
        "competence_month": competence
    })

    entries = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["transaction_id"] = str(doc["transaction_id"])
        entries.append(doc)

    return entries

@router.get("/entries/card/{account_id}/{year}/{month}")
async def card_statement(
    account_id: str,
    household_id: str,
    year: int,
    month: int
):
    competence = f"{year}-{str(month).zfill(2)}"

    cursor = db.transaction_entries.find({
        "household_id": ObjectId(household_id),
        "account_id": ObjectId(account_id),
        "competence_month": competence
    })

    entries = []
    total = 0

    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        total += doc["amount"]
        entries.append(doc)

    return {
        "competence_month": competence,
        "total": round(total, 2),
        "entries": entries
    }

@router.patch("/entries/{entry_id}/pay")
async def mark_entry_as_paid(entry_id: str):
    result = await db.transaction_entries.update_one(
        {"_id": ObjectId(entry_id)},
        {"$set": {"status": "paid"}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")

    return {"message": "Lançamento marcado como pago"}
