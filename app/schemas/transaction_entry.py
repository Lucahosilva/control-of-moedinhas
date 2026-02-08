# schemas/transaction_entry.py
from app.schemas.base import MongoBaseModel, PyObjectId
from datetime import date
from pydantic import Field

class TransactionEntryCreate(MongoBaseModel):
    transaction_id: PyObjectId | None = None
    description: str
    amount: float
    competence_month: str  # YYYY-MM
    due_date: date

    status: str = "open"  # open | paid
    payment_method: str
    account_id: PyObjectId
    category_id: PyObjectId
    household_id: PyObjectId
