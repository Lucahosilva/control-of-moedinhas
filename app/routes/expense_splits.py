from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from datetime import datetime

from app.db.mongo import db
from app.schemas.expense_split import ExpenseSplitCreate
from app.services.expense_split_service import ExpenseSplitService

router = APIRouter(prefix="/expense-splits", tags=["ExpenseSplits"])

@router.post("/", status_code=201, response_model=dict)
async def create_expense_split(payload: ExpenseSplitCreate):
    """Criar uma divisão de despesa entre usuários"""
    try:
        # Validar household
        household = await db.households.find_one({"_id": ObjectId(payload.household_id)})
        if not household:
            raise HTTPException(status_code=404, detail="Domicílio não encontrado")
        
        # Validar usuários
        for user in payload.split_users:
            user_doc = await db.users.find_one({"_id": ObjectId(user.user_id)})
            if not user_doc:
                raise HTTPException(status_code=404, detail=f"Usuário {user.user_id} não encontrado")
        
        # Criar registro de divisão
        split_data = ExpenseSplitService.create_split_record(
            transaction_id=ObjectId(payload.transaction_id) if payload.transaction_id else None,
            household_id=ObjectId(payload.household_id),
            split_type=payload.split_type,
            split_users=payload.split_users,
            total_amount=sum(u.amount or u.percentage or 0 for u in payload.split_users),
            description=payload.description
        )
        
        result = await db.expense_splits.insert_one(split_data)
        
        return {
            "message": "Divisão de despesa criada com sucesso",
            "split_id": str(result.inserted_id),
            "household_id": str(payload.household_id),
            "split_type": payload.split_type,
            "users_count": len(payload.split_users)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar divisão: {str(e)}")


@router.get("/", response_model=List[dict])
async def list_expense_splits(household_id: str = None, settled: bool = None):
    """Listar divisões de despesas"""
    try:
        query = {}
        
        if household_id:
            query["household_id"] = ObjectId(household_id)
        
        if settled is not None:
            query["settled"] = settled
        
        cursor = db.expense_splits.find(query)
        splits = []
        
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            if doc.get("transaction_id"):
                doc["transaction_id"] = str(doc["transaction_id"])
            doc["household_id"] = str(doc["household_id"])
            
            # Converter user_ids para string
            if "split_users" in doc:
                for user in doc["split_users"]:
                    user["user_id"] = str(user["user_id"])
            
            splits.append(doc)
        
        return splits
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar divisões: {str(e)}")


@router.get("/{split_id}", response_model=dict)
async def get_expense_split(split_id: str):
    """Obter detalhes de uma divisão de despesa"""
    try:
        split = await db.expense_splits.find_one({"_id": ObjectId(split_id)})
        
        if not split:
            raise HTTPException(status_code=404, detail="Divisão não encontrada")
        
        split["_id"] = str(split["_id"])
        if split.get("transaction_id"):
            split["transaction_id"] = str(split["transaction_id"])
        split["household_id"] = str(split["household_id"])
        
        # Converter user_ids para string e adicionar nomes
        if "split_users" in split:
            for user in split["split_users"]:
                user_id = user["user_id"]
                user["user_id"] = str(user_id)
                
                # Buscar nome do usuário
                user_doc = await db.users.find_one({"_id": user_id})
                if user_doc:
                    user["user_name"] = user_doc.get("name", "Desconhecido")
        
        return split
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter divisão: {str(e)}")


@router.post("/{split_id}/settle", response_model=dict)
async def settle_expense_split(split_id: str):
    """Marcar uma divisão como resolvida"""
    try:
        result = await db.expense_splits.update_one(
            {"_id": ObjectId(split_id)},
            {"$set": {"settled": True}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Divisão não encontrada")
        
        return {
            "message": "Divisão marcada como resolvida",
            "split_id": split_id
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao resolver divisão: {str(e)}")


@router.get("/household/{household_id}/balance", response_model=dict)
async def get_household_balance(household_id: str):
    """
    Calcular quanto cada usuário deve para cada outro no household
    Mostra quem deve pagar para quem
    """
    try:
        # Validar household
        household = await db.households.find_one({"_id": ObjectId(household_id)})
        if not household:
            raise HTTPException(status_code=404, detail="Domicílio não encontrado")
        
        # Buscar todas as divisões não resolvidas
        cursor = db.expense_splits.find({
            "household_id": ObjectId(household_id),
            "settled": False
        })
        
        splits = []
        async for doc in cursor:
            splits.append(doc)
        
        # Calcular balanço
        balances = ExpenseSplitService.calculate_balance(splits)
        
        # Enriquecer com nomes dos usuários
        result_balance = {}
        for user_id, amount in balances.items():
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
            user_name = user_doc.get("name", "Desconhecido") if user_doc else "Desconhecido"
            result_balance[user_id] = {
                "user_name": user_name,
                "amount": round(amount, 2),
                "status": "deve pagar" if amount > 0 else ("deve receber" if amount < 0 else "quitado")
            }
        
        return {
            "household_id": household_id,
            "balances": result_balance,
            "total_pending": len([b for b in result_balance.values() if b["amount"] != 0])
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular balanço: {str(e)}")


@router.get("/user/{user_id}/balance", response_model=dict)
async def get_user_balance(user_id: str, household_id: str = None):
    """Obter balanço de um usuário específico"""
    try:
        # Validar usuário
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        household_id = household_id or str(user_doc["household_id"])
        
        # Buscar todas as divisões do usuário
        cursor = db.expense_splits.find({
            "household_id": ObjectId(household_id),
            "settled": False,
            "split_users.user_id": ObjectId(user_id)
        })
        
        splits = []
        async for doc in cursor:
            splits.append(doc)
        
        # Calcular balanço geral
        balances = ExpenseSplitService.calculate_balance(splits)
        user_balance = balances.get(user_id, 0)
        
        # Detalhes de cada divisão
        divisions = []
        for split in splits:
            for user in split.get("split_users", []):
                if str(user["user_id"]) == user_id:
                    divisions.append({
                        "split_id": str(split["_id"]),
                        "description": split.get("description", ""),
                        "amount": user.get("amount", 0),
                        "paid_by_user": user.get("paid", False),
                        "created_at": split.get("created_at")
                    })
        
        return {
            "user_id": user_id,
            "user_name": user_doc.get("name"),
            "household_id": household_id,
            "total_balance": round(user_balance, 2),
            "status": "deve pagar" if user_balance > 0 else ("deve receber" if user_balance < 0 else "quitado"),
            "divisions_count": len(divisions),
            "divisions": divisions
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter balanço: {str(e)}")
