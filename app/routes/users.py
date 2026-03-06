from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId

from app.db.mongo import db
from app.schemas.user import UserCreate

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", status_code=201, response_model=dict)
async def create_user(payload: UserCreate):
    """Criar um novo usuário em um centro de custo"""
    try:
        
        # TODO: Hash da senha
        user_data = {
            "name": payload.name,
            "email": payload.email,
            "password_hash": payload.password,  # TODO: Implementar hash
            "role": "member" 
            }
        
        # Verificar se email já existe
        existing = await db.users.find_one({"email": payload.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        
        result = await db.users.insert_one(user_data)
        
        
        return {
            "message": "Usuário criado com sucesso",
            "user_id": str(result.inserted_id),
            "name": payload.name,
            "email": payload.email,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")


@router.get("/", response_model=List[dict])
async def list_users(cost_center_id: str = None):
    """Listar usuários (opcionalmente filtrados por cost_center_id)"""
    try:
        cursor = db.users.find()
        
        users = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
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
        user.pop("password_hash", None)
        
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter usuário: {str(e)}")


@router.get("/cost-center/{cost_center_id}/members", response_model=List[dict])
async def get_cost_center_members(cost_center_id: str):
    """Obter todos os membros de um cost_center"""
    try:
        cursor = db.users.find({"cost_center_id": ObjectId(cost_center_id)})
        
        users = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["cost_center_id"] = str(doc["cost_center_id"])
            doc.pop("password_hash", None)
            users.append(doc)
        
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter membros: {str(e)}")
