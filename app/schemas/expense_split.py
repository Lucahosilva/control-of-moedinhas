# schemas/expense_split.py
from typing import List
from app.schemas.base import MongoBaseModel, PyObjectId

class ExpenseSplitUser(MongoBaseModel):
    """Representa um usuário e sua parte da despesa"""
    user_id: PyObjectId
    amount: float
    paid_by_user: bool = False  # Se este usuário foi quem pagou

class ExpenseSplitCreate(MongoBaseModel):
    """Schema para criar uma divisão de despesa"""
    transaction_id: PyObjectId | None = None
    household_id: PyObjectId
    
    # Usuários envolvidos na divisão
    split_users: List[ExpenseSplitUser]
    
    # Método de divisão
    split_type: str  # "equal" | "custom" | "percentage"
    
    # Descrição
    description: str = ""

class ExpenseSplitDB(ExpenseSplitCreate):
    """Schema do banco de dados com informações adicionais"""
    id: PyObjectId | None = None
    created_at: str = ""  # ISO format datetime
    settled: bool = False  # Se a divisão foi resolvida/acertada
