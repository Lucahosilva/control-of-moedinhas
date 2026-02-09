from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
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
            "cost_center_id": ObjectId(payload.cost_center_id) if payload.cost_center_id else None,
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
async def list_transactions(cost_center_id: str):
    try:
        hid = ObjectId(cost_center_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"cost_center_id '{cost_center_id}' is not a valid ObjectId")

    cursor = db.transactions.find({"cost_center_id": hid})

    transactions = []
    async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            # Convert possible ObjectId fields to strings for JSON serialization
            for fk in ("transaction_id", "account_id", "category_id", "cost_center_id"):
                if fk in doc and doc[fk] is not None:
                    try:
                        doc[fk] = str(doc[fk])
                    except Exception:
                        pass
            # Convert datetime fields
            if "date" in doc and hasattr(doc["date"], "isoformat"):
                doc["date"] = doc["date"].isoformat()

            transactions.append(doc)

    return transactions

@router.get("/entries/month/{year}/{month}")
async def list_entries_by_month(
    cost_center_id: str,
    year: int,
    month: int
):
    competence = f"{year}-{str(month).zfill(2)}"

    try:
        hid = ObjectId(cost_center_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"cost_center_id '{cost_center_id}' is not a valid ObjectId")

    cursor = db.transaction_entries.find({
        "cost_center_id": hid,
        "competence_month": competence
    })

    entries = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        # transaction_id may be ObjectId
        if "transaction_id" in doc and doc["transaction_id"] is not None:
            doc["transaction_id"] = str(doc["transaction_id"])
        # Convert other id fields
        for fk in ("account_id", "category_id", "cost_center_id"):
            if fk in doc and doc[fk] is not None:
                try:
                    doc[fk] = str(doc[fk])
                except Exception:
                    pass
        entries.append(doc)

    return entries

@router.get("/entries/card/{account_id}/{year}/{month}")
async def card_statement(
    account_id: str,
    cost_center_id: str,
    year: int,
    month: int
):
    competence = f"{year}-{str(month).zfill(2)}"

    try:
        hid = ObjectId(cost_center_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"cost_center_id '{cost_center_id}' is not a valid ObjectId")

    try:
        aid = ObjectId(account_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"account_id '{account_id}' is not a valid ObjectId")

    cursor = db.transaction_entries.find({
        "cost_center_id": hid,
        "account_id": aid,
        "competence_month": competence
    })

    entries = []
    total = 0

    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        total += doc["amount"]
        # Convert id fields
        for fk in ("transaction_id", "account_id", "category_id", "cost_center_id"):
            if fk in doc and doc[fk] is not None:
                try:
                    doc[fk] = str(doc[fk])
                except Exception:
                    pass
        # Convert date-like fields if present
        if "due_date" in doc and hasattr(doc["due_date"], "isoformat"):
            doc["due_date"] = doc["due_date"].isoformat()

        entries.append(doc)

    return {
        "competence_month": competence,
        "total": round(total, 2),
        "entries": entries
    }

@router.patch("/entries/{entry_id}/pay")
async def mark_entry_as_paid(entry_id: str):
    try:
        eid = ObjectId(entry_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"entry_id '{entry_id}' is not a valid ObjectId")

    result = await db.transaction_entries.update_one(
        {"_id": eid},
        {"$set": {"status": "paid"}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")

    return {"message": "Lançamento marcado como pago"}
