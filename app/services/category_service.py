
from typing import List
from bson import ObjectId
from fastapi import HTTPException

from app.db.mongo import db
from app.schemas.category import CategoryCreate



class CategoryService:

    async def create_category(self, payload: CategoryCreate):
        # TODO: Implementar lógica para criar categoria evitando duplicar

        self._cost_center_exists(payload.cost_center_id)

        # Validar type
        if payload.type not in ["income", "expense"]:
            raise HTTPException(status_code=400, detail="type deve ser 'income' ou 'expense'")
        
        self._category_exists(payload.name, payload.cost_center_id)

        category_data = {
            "name": payload.name,
            "type": payload.type,
            "cost_center_id": ObjectId(payload.cost_center_id)
        }
        
        result = await db.categories.insert_one(category_data)
        
        return {
            "message": "Categoria criada com sucesso",
            "category_id": str(result.inserted_id),
            "name": payload.name,
            "type": payload.type,
            "cost_center_id": str(payload.cost_center_id)}





    async def _cost_center_exists(self, cost_center_id: str) -> bool:
            cost_center = await db.cost_centers.find_one({"_id": ObjectId(cost_center_id)})
            if not cost_center:
                raise HTTPException(status_code=404, detail="Centro de custo não encontrado")
            

    async def _category_exists(self, name: str, cost_center_id: str) -> bool:
            category = await db.categories.find_one({
                "name": name,
                "cost_center_id": ObjectId(cost_center_id)
            })
            if category:
                raise HTTPException(status_code=400, detail="Categoria com esse nome já existe para este centro de custo")