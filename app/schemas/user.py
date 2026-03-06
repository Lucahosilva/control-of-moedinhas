# schemas/user.py
from app.schemas.base import MongoBaseModel, PyObjectId

class UserCreate(MongoBaseModel):
    name: str
    email: str
    password: str

class UserDB(MongoBaseModel):
    name: str
    email: str
    password_hash: str
    role: str = "member"  # admin | member
