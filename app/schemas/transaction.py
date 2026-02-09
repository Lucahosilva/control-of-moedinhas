# app/schemas/transaction.py
from datetime import date
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, field_validator, model_validator


class FlowType(str, Enum):
    income = "income"
    expense = "expense"


class TransactionType(str, Enum):
    single = "single"
    installment = "installment"
    recurring = "recurring"


class PaymentMethodType(str, Enum):
    cash = "cash"
    debit = "debit"
    credit_card = "credit_card"
    pix = "pix"


class PaymentMethod(BaseModel):
    type: PaymentMethodType
    closing_day: Optional[int] = None
    due_day: Optional[int] = None


class TransactionCreate(BaseModel):
    description: str
    amount: float

    flow_type: FlowType
    transaction_type: TransactionType

    payment_method: PaymentMethod

    date: date

    # parcelamento
    installments: Optional[int] = None
    total_amount: Optional[float] = None

    # relacionamentos
    account_id: Optional[str] = None
    category_id: Optional[str] = None
    cost_center_id: Optional[str] = None


    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('amount deve ser maior que 0')
        return v

    @model_validator(mode='after')
    def validate_installment_fields(self):
        if self.transaction_type == TransactionType.installment:
            if not self.installments or not self.total_amount:
                raise ValueError('installments e total_amount são obrigatórios para transações parceladas')
        return self

