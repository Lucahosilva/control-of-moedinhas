# schemas/household.py
from typing import List
from app.schemas.base import MongoBaseModel, PyObjectId

class HouseholdCreate(MongoBaseModel):
    name: str

class HouseholdDB(HouseholdCreate):
    members: List[PyObjectId] = []
