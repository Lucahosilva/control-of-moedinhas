from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId

from app.db.mongo import db
from app.schemas.account import AccountCreate
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.post("/", status_code=201, response_model=dict)
async def create_account(payload: AccountCreate):
    """Criar uma nova conta"""
    try:
        
        # Validar type
        valid_types = ["checking", "savings", "credit_card"]
        if payload.type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"type deve ser um de: {', '.join(valid_types)}"
            )
        
        # Validar campos de cartão de crédito
        if payload.type == "credit_card":
            if payload.closing_day is None or payload.due_day is None:
                raise HTTPException(
                    status_code=400,
                    detail="closing_day e due_day são obrigatórios para cartão de crédito"
                )
        
        account_data = {
            "name": payload.name,
            "type": payload.type,
            "initial_balance": payload.initial_balance,
            "current_balance": payload.initial_balance
        }
        
        # Adicionar campos opcionais do cartão
        if payload.closing_day is not None:
            account_data["closing_day"] = payload.closing_day
        if payload.due_day is not None:
            account_data["due_day"] = payload.due_day
        
        result = await db.accounts.insert_one(account_data)
        
        return {
            "message": "Conta criada com sucesso",
            "account_id": str(result.inserted_id),
            "name": payload.name,
            "type": payload.type,
            "initial_balance": payload.initial_balance
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar conta: {str(e)}")


@router.get("/")
async def list_accounts(cost_center_id: str = None):
    """Listar contas"""
    try:
        cursor = db.accounts.find()
        
        accounts = []
        async for doc in cursor:
            # Calcular balance actual (initial_balance será usado como balance se current_balance não existir)
            balance = doc.get("current_balance") or doc.get("initial_balance", 0)
            
            account = {
                "id": str(doc["_id"]),
                "name": doc["name"],
                "type": doc["type"],
                "balance": balance,
                "initial_balance": doc["initial_balance"],
                "closing_day": doc.get("closing_day"),
                "due_day": doc.get("due_day")
            }
            accounts.append(account)
        
        return accounts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar contas: {str(e)}")


@router.get("/{account_id}")
async def get_account(account_id: str):
    """Obter detalhes de uma conta"""
    try:
        account = await db.accounts.find_one({"_id": ObjectId(account_id)})
        
        if not account:
            raise HTTPException(status_code=404, detail="Conta não encontrada")
        
        # Calcular balance
        balance = account.get("current_balance") or account.get("initial_balance", 0)
        
        return {
            "id": str(account["_id"]),
            "name": account["name"],
            "type": account["type"],
            "balance": balance,
            "initial_balance": account["initial_balance"],
            "closing_day": account.get("closing_day"),
            "due_day": account.get("due_day")
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter conta: {str(e)}")

@router.patch("/{account_id}/recalculate-balance")
async def recalculate_account_balance(account_id: str):
    """
    Recalcula o saldo da conta baseado nas transações com vencimento passado.
    Útil para sincronizar o saldo em caso de inconsistências.
    """
    try:
        # Verificar se a conta existe
        account = await db.accounts.find_one({"_id": ObjectId(account_id)})
        if not account:
            raise HTTPException(status_code=404, detail="Conta não encontrada")

        # Calcular o novo saldo
        transaction_service = TransactionService()
        initial_balance = account.get("initial_balance", 0)
        new_balance = await transaction_service.calculate_account_balance(db, account_id, initial_balance)

        # Atualizar o saldo da conta
        await db.accounts.update_one(
            {"_id": ObjectId(account_id)},
            {"$set": {"current_balance": new_balance}}
        )

        return {
            "message": "Saldo recalculado com sucesso",
            "account_id": account_id,
            "new_balance": new_balance
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recalcular saldo: {str(e)}")