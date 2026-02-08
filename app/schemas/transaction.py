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


class SplitUser(BaseModel):
    """Usuário envolvido em uma divisão de despesa"""
    user_id: str
    amount: Optional[float] = None  # Para custom split
    percentage: Optional[float] = None  # Para percentage split
    paid: bool = False  # Se este usuário foi quem pagou


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
    household_id: Optional[str] = None

    # divisão de despesas (opcional)
    split_type: Optional[str] = None  # "equal" | "custom" | "percentage" | None (sem divisão)
    split_users: Optional[List[SplitUser]] = None  # Usuários envolvidos na divisão
    paid_by_user_id: Optional[str] = None  # Usuário que pagou (para rastreamento)

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

    @model_validator(mode='after')
    def validate_split_fields(self):
        if self.split_type:
            if not self.split_users or len(self.split_users) < 2:
                raise ValueError('split_users deve conter pelo menos 2 usuários para divisão')
            
            if self.split_type == "percentage":
                total_percentage = sum(u.percentage or 0 for u in self.split_users)
                if abs(total_percentage - 100) > 0.01:
                    raise ValueError('percentuais devem somar 100%')
            
            if self.split_type == "custom":
                total_amount = sum(u.amount or 0 for u in self.split_users)
                if abs(total_amount - self.amount) > 0.01:
                    raise ValueError('valores customizados devem somar ao amount total')
        
        return self
