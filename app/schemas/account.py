# schemas/account.py
from app.schemas.base import MongoBaseModel, PyObjectId
from typing import Optional

class AccountCreate(MongoBaseModel):
    name: str
    type: str  # checking | savings | credit_card
    initial_balance: float
    household_id: PyObjectId

    # só se for cartão
    closing_day: Optional[int] = None
    due_day: Optional[int] = None
