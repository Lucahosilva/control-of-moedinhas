from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId

from app.db.mongo import db
from app.schemas.household import HouseholdCreate, HouseholdDB

router = APIRouter(prefix="/households", tags=["Households"])

@router.post("/", status_code=201, response_model=dict)
async def create_household(payload: HouseholdCreate):
    """Criar um novo domicílio"""
    try:
        household_data = {
            "name": payload.name,
            "members": []
        }
        
        result = await db.households.insert_one(household_data)
        
        return {
            "message": "Domicílio criado com sucesso",
            "household_id": str(result.inserted_id),
            "name": payload.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar domicílio: {str(e)}")


@router.get("/", response_model=List[dict])
async def list_households():
    """Listar todos os domicílios"""
    try:
        cursor = db.households.find()
        households = []
        
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            households.append(doc)
        
        return households
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar domicílios: {str(e)}")


@router.get("/{household_id}", response_model=dict)
async def get_household(household_id: str):
    """Obter detalhes de um domicílio"""
    try:
        household = await db.households.find_one({"_id": ObjectId(household_id)})
        
        if not household:
            raise HTTPException(status_code=404, detail="Domicílio não encontrado")
        
        household["_id"] = str(household["_id"])
        household["members"] = [str(m) for m in household.get("members", [])]
        
        return household
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter domicílio: {str(e)}")
