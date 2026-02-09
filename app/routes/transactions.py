from fastapi import APIRouter, HTTPException
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date
from pydantic import BaseModel

from app.db.mongo import db
from app.schemas.transaction import TransactionCreate
from app.schemas.transaction_entry import TransactionEntryCreate
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


class DeleteTransactionsFilter(BaseModel):
    """Filtros para deletar múltiplas transações"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    account_id: Optional[str] = None
    cost_center_id: Optional[str] = None
    user_id: Optional[str] = None

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

@router.delete("/{transaction_id}", status_code=200)
async def delete_transaction(transaction_id: str):
    """
    Deleta uma transação e todos os seus lançamentos associados.
    """
    try:
        tid = ObjectId(transaction_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"transaction_id '{transaction_id}' is not a valid ObjectId")

    # Deleta a transação
    transaction_result = await db.transactions.delete_one({"_id": tid})
    
    if transaction_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    # Deleta todos os lançamentos associados
    entries_result = await db.transaction_entries.delete_many({"transaction_id": tid})

    return {
        "message": "Transação deletada com sucesso",
        "transaction_id": transaction_id,
        "entries_deleted": entries_result.deleted_count
    }

@router.delete("/", status_code=200)
async def delete_multiple_transactions(filters: DeleteTransactionsFilter):
    """
    Deleta múltiplas transações e seus lançamentos associados com base em filtros.
    
    Filtros disponíveis:
    - start_date: Data inicial do range (formato: YYYY-MM-DD)
    - end_date: Data final do range (formato: YYYY-MM-DD)
    - account_id: ID da conta
    - cost_center_id: ID do centro de custo
    - user_id: ID do usuário
    
    Exemplo de payload:
    {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "cost_center_id": "67a1b2c3d4e5f6g7h8i9j0k1"
    }
    """
    
    # Verifica se pelo menos um filtro foi fornecido
    if not any([filters.start_date, filters.end_date, filters.account_id, 
                filters.cost_center_id, filters.user_id]):
        raise HTTPException(
            status_code=400, 
            detail="É necessário fornecer pelo menos um filtro (start_date, end_date, account_id, cost_center_id ou user_id)"
        )

    # Constrói o filtro para a query
    query_filter = {}

    # Filtro por data
    if filters.start_date or filters.end_date:
        date_filter = {}
        if filters.start_date:
            date_filter["$gte"] = datetime.combine(filters.start_date, datetime.min.time())
        if filters.end_date:
            date_filter["$lte"] = datetime.combine(filters.end_date, datetime.max.time())
        query_filter["date"] = date_filter

    # Filtro por conta
    if filters.account_id:
        try:
            query_filter["account_id"] = ObjectId(filters.account_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail=f"account_id '{filters.account_id}' is not a valid ObjectId")

    # Filtro por centro de custo
    if filters.cost_center_id:
        try:
            query_filter["cost_center_id"] = ObjectId(filters.cost_center_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail=f"cost_center_id '{filters.cost_center_id}' is not a valid ObjectId")

    # Filtro por usuário
    if filters.user_id:
        try:
            query_filter["user_id"] = ObjectId(filters.user_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail=f"user_id '{filters.user_id}' is not a valid ObjectId")

    try:
        # Encontra as transações que correspondem aos filtros
        transactions_cursor = db.transactions.find(query_filter)
        transaction_ids = []
        async for doc in transactions_cursor:
            transaction_ids.append(doc["_id"])

        if not transaction_ids:
            raise HTTPException(status_code=404, detail="Nenhuma transação encontrada com os filtros fornecidos")

        # Deleta as transações
        transactions_result = await db.transactions.delete_many({"_id": {"$in": transaction_ids}})

        # Deleta todos os lançamentos associados
        entries_result = await db.transaction_entries.delete_many({"transaction_id": {"$in": transaction_ids}})

        return {
            "message": "Transações deletadas com sucesso",
            "transactions_deleted": transactions_result.deleted_count,
            "entries_deleted": entries_result.deleted_count,
            "filters_applied": filters.model_dump(exclude_none=True)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar transações: {str(e)}")
