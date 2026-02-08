from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId

from app.db.mongo import db
from app.schemas.user import UserCreate

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", status_code=201, response_model=dict)
async def create_user(payload: UserCreate):
    """Criar um novo usuário em um household"""
    try:
        # Validar household
        household = await db.households.find_one({"_id": ObjectId(payload.household_id)})
        if not household:
            raise HTTPException(status_code=404, detail="Domicílio não encontrado")
        
        # TODO: Hash da senha
        user_data = {
            "name": payload.name,
            "email": payload.email,
            "password_hash": payload.password,  # TODO: Implementar hash
            "role": "member",
            "household_id": ObjectId(payload.household_id)
        }
        
        # Verificar se email já existe
        existing = await db.users.find_one({"email": payload.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        result = await db.users.insert_one(user_data)
        
        # Adicionar usuário aos members do household
        await db.households.update_one(
            {"_id": ObjectId(payload.household_id)},
            {"$push": {"members": result.inserted_id}}
        )
        
        return {
            "message": "Usuário criado com sucesso",
            "user_id": str(result.inserted_id),
            "name": payload.name,
            "email": payload.email,
            "household_id": payload.household_id
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")


@router.get("/", response_model=List[dict])
async def list_users(household_id: str = None):
    """Listar usuários (opcionalmente filtrados por household_id)"""
    try:
        if household_id:
            cursor = db.users.find({"household_id": ObjectId(household_id)})
        else:
            cursor = db.users.find()
        
        users = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["household_id"] = str(doc["household_id"])
            # Não retornar senha
            doc.pop("password_hash", None)
            users.append(doc)
        
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")


@router.get("/{user_id}", response_model=dict)
async def get_user(user_id: str):
    """Obter detalhes de um usuário"""
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        user["_id"] = str(user["_id"])
        user["household_id"] = str(user["household_id"])
        # Não retornar senha
        user.pop("password_hash", None)
        
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter usuário: {str(e)}")


@router.get("/household/{household_id}/members", response_model=List[dict])
async def get_household_members(household_id: str):
    """Obter todos os membros de um household"""
    try:
        cursor = db.users.find({"household_id": ObjectId(household_id)})
        
        users = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["household_id"] = str(doc["household_id"])
            doc.pop("password_hash", None)
            users.append(doc)
        
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter membros: {str(e)}")
