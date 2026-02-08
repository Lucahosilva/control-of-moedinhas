from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId

from app.db.mongo import db
from app.schemas.category import CategoryCreate

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", status_code=201, response_model=dict)
async def create_category(payload: CategoryCreate):
    """Criar uma nova categoria"""
    try:
        # Validar que household_id existe
        household = await db.households.find_one({"_id": ObjectId(payload.household_id)})
        if not household:
            raise HTTPException(status_code=404, detail="Domicílio não encontrado")
        
        # Validar type
        if payload.type not in ["income", "expense"]:
            raise HTTPException(status_code=400, detail="type deve ser 'income' ou 'expense'")
        
        category_data = {
            "name": payload.name,
            "type": payload.type,
            "household_id": ObjectId(payload.household_id)
        }
        
        result = await db.categories.insert_one(category_data)
        
        return {
            "message": "Categoria criada com sucesso",
            "category_id": str(result.inserted_id),
            "name": payload.name,
            "type": payload.type,
            "household_id": str(payload.household_id)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar categoria: {str(e)}")


@router.get("/", response_model=List[dict])
async def list_categories(household_id: str = None):
    """Listar categorias (opcionalmente filtradas por household_id)"""
    try:
        if household_id:
            cursor = db.categories.find({"household_id": ObjectId(household_id)})
        else:
            cursor = db.categories.find()
        
        categories = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["household_id"] = str(doc["household_id"])
            categories.append(doc)
        
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar categorias: {str(e)}")


@router.get("/{category_id}", response_model=dict)
async def get_category(category_id: str):
    """Obter detalhes de uma categoria"""
    try:
        category = await db.categories.find_one({"_id": ObjectId(category_id)})
        
        if not category:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        
        category["_id"] = str(category["_id"])
        category["household_id"] = str(category["household_id"])
        
        return category
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter categoria: {str(e)}")
