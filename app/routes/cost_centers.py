from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId

from app.db.mongo import db
from app.schemas.cost_center import CostCenterCreate

router = APIRouter(prefix="/cost-centers", tags=["Cost Centers"])

@router.post("/", status_code=201, response_model=dict)
async def create_cost_center(payload: CostCenterCreate):
    """Criar um novo centro de custo"""
    try:
        cost_center_data = {
            "name": payload.name
        }
        
        result = await db.cost_centers.insert_one(cost_center_data)
        
        return {
            "message": "Centro de custo criado com sucesso",
            "cost_center_id": str(result.inserted_id),
            "name": payload.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar centro de custo: {str(e)}")


@router.get("/", response_model=List[dict])
async def list_cost_centers():
    """Listar todos os centros de custo"""
    try:
        cursor = db.cost_centers.find()
        print("Chegou aqui")
        cost_centers = []
        print("cursor:", cursor)
        
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            cost_centers.append(doc)
        
        return cost_centers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar centros de custo: {str(e)}")


@router.get("/{cost_center_id}", response_model=dict)
async def get_cost_center(cost_center_id: str):
    """Obter detalhes de um centro de custo"""
    try:
        cost_center = await db.cost_centers.find_one({"_id": ObjectId(cost_center_id)})
        
        if not cost_center:
            raise HTTPException(status_code=404, detail="Centro de custo não encontrado")
        
        cost_center["_id"] = str(cost_center["_id"])
        cost_center["members"] = [str(m) for m in cost_center.get("members", [])]
        
        return cost_center
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter centro de custo: {str(e)}")
