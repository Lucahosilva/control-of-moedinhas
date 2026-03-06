from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId

from app.db.mongo import db
from app.schemas.category import CategoryCreate
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", status_code=201, response_model=dict)
async def create_category(payload: CategoryCreate):
    """Criar uma nova categoria"""
    try:

        service = CategoryService()
        return await service.create_category(payload)
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar categoria: {str(e)}")


@router.get("/", response_model=List[dict])
async def list_categories(cost_center_id: str = None):
    """Listar categorias (opcionalmente filtradas por cost_center_id)"""
    try:
        cursor = db.categories.find()
        
        categories = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
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
        
        return category
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter categoria: {str(e)}")
