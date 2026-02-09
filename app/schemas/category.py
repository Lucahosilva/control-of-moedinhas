# schemas/category.py
from app.schemas.base import MongoBaseModel, PyObjectId

class CategoryCreate(MongoBaseModel):
    name: str
    type: str  # income | expense
    cost_center_id: PyObjectId
