# schemas/category.py
from app.schemas.base import MongoBaseModel, PyObjectId

class CategoryCreate(MongoBaseModel):
    name: str
    type: str  # income | expense
    household_id: PyObjectId
