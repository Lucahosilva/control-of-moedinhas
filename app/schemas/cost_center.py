# schemas/cost_center.py
from typing import List
from app.schemas.base import MongoBaseModel, PyObjectId

class CostCenterCreate(MongoBaseModel):
    name: str

