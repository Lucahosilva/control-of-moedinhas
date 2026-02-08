# services/expense_split_service.py
from typing import List, Dict
from bson import ObjectId
from datetime import datetime
from app.schemas.transaction import SplitUser

class ExpenseSplitService:
    """Serviço para gerenciar divisões de despesas entre usuários"""

    @staticmethod
    def calculate_split(
        total_amount: float,
        split_type: str,
        split_users: List[SplitUser]
    ) -> Dict[str, float]:
        """
        Calcula como a despesa deve ser dividida
        
        Args:
            total_amount: Valor total da despesa
            split_type: "equal" | "custom" | "percentage"
            split_users: Lista de usuários envolvidos
        
        Returns:
            Dicionário {user_id: amount_a_pagar}
        """
        split_result = {}
        
        if split_type == "equal":
            # Divisão igual entre todos os usuários
            amount_per_person = total_amount / len(split_users)
            for user in split_users:
                split_result[user.user_id] = round(amount_per_person, 2)
        
        elif split_type == "custom":
            # Divisão customizada (cada um paga um valor específico)
            for user in split_users:
                split_result[user.user_id] = round(user.amount, 2)
        
        elif split_type == "percentage":
            # Divisão por percentual
            for user in split_users:
                amount = (total_amount * user.percentage) / 100
                split_result[user.user_id] = round(amount, 2)
        
        return split_result

    @staticmethod
    def create_split_record(
        transaction_id: ObjectId,
        household_id: ObjectId,
        split_type: str,
        split_users: List[SplitUser],
        total_amount: float,
        description: str = ""
    ) -> Dict:
        """
        Cria um registro de divisão de despesa
        
        Returns:
            Dicionário com dados da divisão
        """
        split_data = {
            "transaction_id": transaction_id,
            "household_id": household_id,
            "split_type": split_type,
            "total_amount": total_amount,
            "created_at": datetime.now().isoformat(),
            "description": description,
            "settled": False,
            "split_users": []
        }
        
        # Calcular divisão
        split_amounts = ExpenseSplitService.calculate_split(
            total_amount,
            split_type,
            split_users
        )
        
        # Adicionar usuários com seus valores
        for user in split_users:
            split_users_data = {
                "user_id": ObjectId(user.user_id),
                "amount": split_amounts[user.user_id],
                "paid": user.paid
            }
            split_data["split_users"].append(split_users_data)
        
        return split_data

    @staticmethod
    def calculate_balance(expense_splits: List[Dict]) -> Dict[str, float]:
        """
        Calcula quanto cada usuário deve para cada outro
        
        Args:
            expense_splits: Lista de divisões de despesas
        
        Returns:
            Dicionário com balanço entre usuários {user_id: amount}
        """
        balances = {}
        
        for split in expense_splits:
            if split.get("settled"):
                continue  # Pular divisões já resolvidas
            
            # Quem pagou
            payer = None
            for user in split.get("split_users", []):
                if user.get("paid"):
                    payer = str(user["user_id"])
                    break
            
            if not payer:
                continue
            
            # Quanto cada um deve pagar
            for user in split.get("split_users", []):
                user_id = str(user["user_id"])
                amount = user.get("amount", 0)
                
                if user_id == payer:
                    # Quem pagou
                    if user_id not in balances:
                        balances[user_id] = 0
                    # Subtrair o que outros devem pagar
                    balances[user_id] -= (split.get("total_amount", 0) - amount)
                else:
                    # Quem deve pagar
                    if user_id not in balances:
                        balances[user_id] = 0
                    balances[user_id] += amount
        
        return balances
