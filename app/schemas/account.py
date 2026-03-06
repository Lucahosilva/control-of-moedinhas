# schemas/account.py
from app.schemas.base import MongoBaseModel, PyObjectId
from pydantic import BaseModel
from typing import Optional

class AccountCreate(MongoBaseModel):
    name: str
    type: str  # checking | savings | credit_card
    initial_balance: float

    # só se for cartão
    closing_day: Optional[int] = None
    due_day: Optional[int] = None


class AccountResponse(BaseModel):
    id: str
    name: str
    type: str
    balance: float
    initial_balance: float
    closing_day: Optional[int] = None
    due_day: Optional[int] = None
