from fastapi import APIRouter, HTTPException
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, date
from pydantic import BaseModel
import logging

from app.db.mongo import db
from app.schemas.transaction import TransactionCreate
from app.schemas.transaction_entry import TransactionEntryCreate
from app.services.transaction_service import TransactionService
from app.core.config import settings

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)

# Handler para console (se não houver já)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class DeleteTransactionsFilter(BaseModel):
    """Filtros para deletar múltiplas transações"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    account_id: Optional[str] = None
    cost_center_id: Optional[str] = None
    user_id: Optional[str] = None

@router.post("/", status_code=201)
async def create_transaction(payload: TransactionCreate):
    logger.debug(f"Iniciando criação de transação: {payload.description}, value: {payload.total_amount}")
    try:
        # Calcula o amount baseado no tipo de transação
        if payload.transaction_type == "installment":
            amount = round(payload.total_amount / payload.installments, 2)
        else:
            amount = payload.total_amount
        
        logger.debug(f"Amount calculado: {amount}")
        
        # Converte IDs string para ObjectId
        transaction_data = {
            "description": payload.description,
            "amount": amount,
            "total_amount": payload.total_amount,
            "flow_type": payload.flow_type.value,
            "transaction_type": payload.transaction_type.value,
            "payment_method": payload.payment_method.model_dump(),
            "date": datetime.combine(payload.date, datetime.min.time()),
            "status": "completed",
            "account_id": ObjectId(payload.account_id) if payload.account_id else None,
            "category_id": ObjectId(payload.category_id) if payload.category_id else None,
            "cost_center_id": ObjectId(payload.cost_center_id) if payload.cost_center_id else None,
        }
        
        if payload.transaction_type == "installment":
            transaction_data["installments"] = payload.installments

        logger.debug(f"Dados da transação convertidos: {transaction_data}")
        result = await db.transactions.insert_one(transaction_data)
        transaction_id = result.inserted_id
        logger.debug(f"Transação inserida com ID: {transaction_id}")

        # 2. gera lançamentos
        entries = TransactionService.generate_entries(payload)
        logger.debug(f"Gerados {len(entries)} lançamentos")

        # 3. salva lançamentos
        entries_to_insert = []
        for entry in entries:
            entry_dict = entry.model_dump(exclude={"id"})
            entry_dict["transaction_id"] = transaction_id
            entry_dict["status"] = "completed"
            entry_dict["flow_type"] = payload.flow_type.value

            entry_dict["due_date"] = datetime.combine(entry_dict["due_date"], datetime.min.time())
            entries_to_insert.append(entry_dict)

        if entries_to_insert:
            await db.transaction_entries.insert_many(entries_to_insert)
            logger.debug(f"{len(entries_to_insert)} lançamentos inseridos no banco")

        # 4. Atualizar saldo da conta se houver account_id
        if payload.account_id:
            try:
                account_id_obj = ObjectId(payload.account_id)
                logger.debug(f"Account ID string: {payload.account_id}, ObjectId: {account_id_obj}")
                account = await db.accounts.find_one({"_id": account_id_obj})
                if account:
                    initial_balance = account.get("initial_balance", 0)
                    logger.debug(f"Iniciando cálculo de saldo para conta {payload.account_id}, initial_balance: {initial_balance}")
                    new_balance = await TransactionService.calculate_account_balance(
                        db, account_id_obj, initial_balance
                    )
                    logger.debug(f"Saldo calculado para conta {payload.account_id}: {new_balance}")
                    await db.accounts.update_one(
                        {"_id": account_id_obj},
                        {"$set": {"current_balance": new_balance}}
                    )
                    logger.debug(f"Saldo da conta {payload.account_id} atualizado para: {new_balance}")
                else:
                    logger.warning(f"Conta {payload.account_id} não encontrada")
            except Exception as e:
                logger.error(f"Erro ao atualizar saldo da conta: {str(e)}", exc_info=True)

        logger.info(f"Transação criada com sucesso: {transaction_id}")
        return {
            "message": "Transação criada com sucesso",
            "transaction_id": str(transaction_id),
            "entries_created": len(entries_to_insert)
        }

    except ValueError as e:
        logger.error(f"Erro de validação ao criar transação: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro de validação: {str(e)}")
    except Exception as e:
        logger.error(f"Erro ao criar transação: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar transação: {str(e)}")

@router.get("/")
async def list_transactions():
    cursor = db.transactions.find().limit(100)

    transactions = []
    async for doc in cursor:
        # Buscar categoria se existir
        category_data = None
        if doc.get("category_id"):
            try:
                category = await db.categories.find_one({"_id": doc["category_id"]})
                if category:
                    category_data = {
                        "id": str(category["_id"]),
                        "name": category.get("name", "Sem categoria"),
                        "type": category.get("type", "expense")
                    }
            except Exception as e:
                logger.error(f"Erro ao buscar categoria: {e}")

        # Converter datetime para ISO string
        date_str = doc["date"].isoformat() if hasattr(doc["date"], "isoformat") else str(doc["date"])

        transaction = {
            "id": str(doc["_id"]),
            "description": doc["description"],
            "amount": doc["amount"],
            "total_amount": doc["total_amount"],
            "flow_type": doc["flow_type"],
            "transaction_type": doc["transaction_type"],
            "date": date_str,
            "status": doc.get("status", "completed"),
            "category": category_data,
            "account_id": str(doc["account_id"]) if doc.get("account_id") else None,
            "cost_center_id": str(doc["cost_center_id"]) if doc.get("cost_center_id") else None,
        }
        transactions.append(transaction)

    return transactions

@router.get("/entries/month/{year}/{month}")
async def list_entries_by_month(
    cost_center_id: str,
    year: int,
    month: int
):
    competence = f"{year}-{str(month).zfill(2)}"
    logger.debug(f"Listando lançamentos mensais - cost_center_id: {cost_center_id}, competence: {competence}")

    try:
        hid = ObjectId(cost_center_id)
    except InvalidId:
        logger.error(f"cost_center_id inválido: {cost_center_id}")
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

    logger.info(f"Retornando {len(entries)} lançamentos para competence: {competence}")
    return entries

@router.get("/entries/card/{account_id}/{year}/{month}")
async def card_statement(
    account_id: str,
    cost_center_id: str,
    year: int,
    month: int
):
    competence = f"{year}-{str(month).zfill(2)}"
    logger.debug(f"Extrato do cartão - account_id: {account_id}, competence: {competence}")

    try:
        hid = ObjectId(cost_center_id)
    except InvalidId:
        logger.error(f"cost_center_id inválido: {cost_center_id}")
        raise HTTPException(status_code=400, detail=f"cost_center_id '{cost_center_id}' is not a valid ObjectId")

    try:
        aid = ObjectId(account_id)
    except InvalidId:
        logger.error(f"account_id inválido: {account_id}")
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

    logger.info(f"Extrato do cartão: {len(entries)} lançamentos, total: {round(total, 2)}")
    return {
        "competence_month": competence,
        "total": round(total, 2),
        "entries": entries
    }

@router.patch("/entries/{entry_id}/pay")
async def mark_entry_as_paid(entry_id: str):
    logger.debug(f"Marcando lançamento {entry_id} como pago")
    try:
        eid = ObjectId(entry_id)
    except InvalidId:
        logger.error(f"entry_id inválido: {entry_id}")
        raise HTTPException(status_code=400, detail=f"entry_id '{entry_id}' is not a valid ObjectId")

    result = await db.transaction_entries.update_one(
        {"_id": eid},
        {"$set": {"status": "paid"}}
    )

    if result.matched_count == 0:
        logger.warning(f"Lançamento não encontrado: {entry_id}")
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")

    logger.info(f"Lançamento marcado como pago: {entry_id}")

    return {"message": "Lançamento marcado como pago"}

@router.delete("/{transaction_id}", status_code=200)
async def delete_transaction(transaction_id: str):
    """
    Deleta uma transação e todos os seus lançamentos associados.
    """
    logger.debug(f"Deletando transação: {transaction_id}")
    try:
        tid = ObjectId(transaction_id)
    except InvalidId:
        logger.error(f"transaction_id inválido: {transaction_id}")
        raise HTTPException(status_code=400, detail=f"transaction_id '{transaction_id}' is not a valid ObjectId")

    # Busca a transação antes de deletá-la para pegar a conta associada
    transaction = await db.transactions.find_one({"_id": tid})
    if not transaction:
        logger.warning(f"Transação não encontrada: {transaction_id}")
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    account_id = transaction.get("account_id")

    # Deleta a transação
    transaction_result = await db.transactions.delete_one({"_id": tid})

    # Deleta todos os lançamentos associados
    entries_result = await db.transaction_entries.delete_many({"transaction_id": tid})
    
    # Atualizar saldo da conta se houver account_id
    if account_id:
        try:
            account = await db.accounts.find_one({"_id": account_id})
            if account:
                initial_balance = account.get("initial_balance", 0)
                new_balance = await TransactionService.calculate_account_balance(
                    db, account_id, initial_balance
                )
                await db.accounts.update_one(
                    {"_id": account_id},
                    {"$set": {"current_balance": new_balance}}
                )
                logger.debug(f"Saldo da conta atualizado após deleção para: {new_balance}")
        except Exception as e:
            logger.error(f"Erro ao atualizar saldo da conta após deleção: {str(e)}")
    
    logger.info(f"Transação deletada: {transaction_id}, {entries_result.deleted_count} lançamentos removidos")
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
    logger.debug(f"Deletando múltiplas transações com filtros: {filters.model_dump(exclude_none=True)}")
    
    # Verifica se pelo menos um filtro foi fornecido
    if not any([filters.start_date, filters.end_date, filters.account_id, 
                filters.cost_center_id, filters.user_id]):
        logger.error("Nenhum filtro fornecido para deleção de múltiplas transações")
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
        logger.debug(f"Filtro de data aplicado: {date_filter}")

    # Filtro por conta
    if filters.account_id:
        try:
            query_filter["account_id"] = ObjectId(filters.account_id)
            logger.debug(f"Filtro de conta aplicado: {filters.account_id}")
        except InvalidId:
            logger.error(f"account_id inválido: {filters.account_id}")
            raise HTTPException(status_code=400, detail=f"account_id '{filters.account_id}' is not a valid ObjectId")

    # Filtro por centro de custo
    if filters.cost_center_id:
        try:
            query_filter["cost_center_id"] = ObjectId(filters.cost_center_id)
            logger.debug(f"Filtro de centro de custo aplicado: {filters.cost_center_id}")
        except InvalidId:
            logger.error(f"cost_center_id inválido: {filters.cost_center_id}")
            raise HTTPException(status_code=400, detail=f"cost_center_id '{filters.cost_center_id}' is not a valid ObjectId")

    # Filtro por usuário
    if filters.user_id:
        try:
            query_filter["user_id"] = ObjectId(filters.user_id)
            logger.debug(f"Filtro de usuário aplicado: {filters.user_id}")
        except InvalidId:
            logger.error(f"user_id inválido: {filters.user_id}")
            raise HTTPException(status_code=400, detail=f"user_id '{filters.user_id}' is not a valid ObjectId")

    try:
        # Encontra as transações que correspondem aos filtros
        logger.debug(f"Buscando transações com filtros: {query_filter}")
        transactions_cursor = db.transactions.find(query_filter)
        transaction_ids = []
        account_ids = set()
        async for doc in transactions_cursor:
            transaction_ids.append(doc["_id"])
            if doc.get("account_id"):
                account_ids.add(doc["account_id"])

        logger.debug(f"Encontradas {len(transaction_ids)} transações para deletar")

        if not transaction_ids:
            logger.warning("Nenhuma transação encontrada com os filtros fornecidos")
            raise HTTPException(status_code=404, detail="Nenhuma transação encontrada com os filtros fornecidos")

        # Deleta as transações
        logger.debug(f"Deletando {len(transaction_ids)} transações")
        transactions_result = await db.transactions.delete_many({"_id": {"$in": transaction_ids}})

        # Deleta todos os lançamentos associados
        logger.debug(f"Deletando lançamentos associados às transações")
        entries_result = await db.transaction_entries.delete_many({"transaction_id": {"$in": transaction_ids}})

        # Atualizar saldo das contas afetadas
        for account_id in account_ids:
            try:
                account = await db.accounts.find_one({"_id": account_id})
                if account:
                    initial_balance = account.get("initial_balance", 0)
                    new_balance = await TransactionService.calculate_account_balance(
                        db, account_id, initial_balance
                    )
                    await db.accounts.update_one(
                        {"_id": account_id},
                        {"$set": {"current_balance": new_balance}}
                    )
                    logger.debug(f"Saldo da conta atualizado após deleção para: {new_balance}")
            except Exception as e:
                logger.error(f"Erro ao atualizar saldo da conta após deleção: {str(e)}")

        logger.info(f"Transações deletadas: {transactions_result.deleted_count}, lançamentos removidos: {entries_result.deleted_count}")
        return {
            "message": "Transações deletadas com sucesso",
            "transactions_deleted": transactions_result.deleted_count,
            "entries_deleted": entries_result.deleted_count,
            "filters_applied": filters.model_dump(exclude_none=True)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar transações: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao deletar transações: {str(e)}")
