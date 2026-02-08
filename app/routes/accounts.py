from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId

from app.db.mongo import db
from app.schemas.account import AccountCreate

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.post("/", status_code=201, response_model=dict)
async def create_account(payload: AccountCreate):
    """Criar uma nova conta"""
    try:
        # Validar household
        household = await db.households.find_one({"_id": ObjectId(payload.household_id)})
        if not household:
            raise HTTPException(status_code=404, detail="Domicílio não encontrado")
        
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
            "current_balance": payload.initial_balance,
            "household_id": ObjectId(payload.household_id)
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
            "initial_balance": payload.initial_balance,
            "household_id": str(payload.household_id)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar conta: {str(e)}")


@router.get("/", response_model=List[dict])
async def list_accounts(household_id: str = None):
    """Listar contas (opcionalmente filtradas por household_id)"""
    try:
        if household_id:
            cursor = db.accounts.find({"household_id": ObjectId(household_id)})
        else:
            cursor = db.accounts.find()
        
        accounts = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["household_id"] = str(doc["household_id"])
            accounts.append(doc)
        
        return accounts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar contas: {str(e)}")


@router.get("/{account_id}", response_model=dict)
async def get_account(account_id: str):
    """Obter detalhes de uma conta"""
    try:
        account = await db.accounts.find_one({"_id": ObjectId(account_id)})
        
        if not account:
            raise HTTPException(status_code=404, detail="Conta não encontrada")
        
        account["_id"] = str(account["_id"])
        account["household_id"] = str(account["household_id"])
        
        return account
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter conta: {str(e)}")
