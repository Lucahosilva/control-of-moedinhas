# services/transaction_service.py
from datetime import date, datetime
from typing import List
from dateutil.relativedelta import relativedelta
from bson import ObjectId

from app.schemas.transaction import TransactionCreate
from app.schemas.transaction_entry import TransactionEntryCreate
from app.services.date_utils import calculate_due_date, competence_month


class TransactionService:

    @staticmethod
    def generate_entries(transaction: TransactionCreate) -> List[TransactionEntryCreate]:
        entries = []

        pm = transaction.payment_method
        start_date = transaction.date

        # =========================
        # SINGLE
        # =========================
        if transaction.transaction_type == "single":
            due = TransactionService._resolve_due_date(start_date, pm)

            entries.append(
                TransactionEntryCreate(
                    transaction_id=None,
                    description=transaction.description,
                    amount=transaction.total_amount,
                    competence_month=competence_month(due),
                    due_date=due,
                    payment_method=pm.type,
                    flow_type=transaction.flow_type.value,
                    account_id=transaction.account_id,
                    category_id=transaction.category_id,
                    cost_center_id=transaction.cost_center_id,
                )
            )

        # =========================
        # INSTALLMENT
        # =========================
        elif transaction.transaction_type == "installment":
            value = round(transaction.total_amount / transaction.installments, 2)

            first_due = TransactionService._resolve_due_date(start_date, pm)

            for i in range(transaction.installments):
                due = first_due + relativedelta(months=i)

                entries.append(
                    TransactionEntryCreate(
                        transaction_id=None,
                        description=f"{transaction.description} {i+1}/{transaction.installments}",
                        amount=value,
                        competence_month=competence_month(due),
                        due_date=due,
                        payment_method=pm.type,
                        flow_type=transaction.flow_type.value,
                        account_id=transaction.account_id,
                        category_id=transaction.category_id,
                        cost_center_id=transaction.cost_center_id,
                    )
                )

        # =========================
        # RECURRING
        # =========================
        elif transaction.transaction_type == "recurring":
            due = TransactionService._resolve_due_date(start_date, pm)

            entries.append(
                TransactionEntryCreate(
                    transaction_id=None,
                    description=transaction.description,
                    amount=transaction.total_amount,
                    competence_month=competence_month(due),
                    due_date=due,
                    payment_method=pm.type,
                    flow_type=transaction.flow_type.value,
                    account_id=transaction.account_id,
                    category_id=transaction.category_id,
                    cost_center_id=transaction.cost_center_id,
                )
            )

        else:
            raise ValueError("transaction_type inválido")

        return entries

    @staticmethod
    def _resolve_due_date(base_date: date, payment_method):
        if payment_method.type == "credit_card":
            return calculate_due_date(
                base_date,
                payment_method.closing_day,
                payment_method.due_day
            )

        return base_date

    @staticmethod
    async def calculate_account_balance(db, account_id, initial_balance):
        """
        Calcula o saldo correto da conta considerando apenas transações com due_date <= hoje.
        
        - Transações com vencimento futuro NÃO são contabilizadas
        - Transações com parcelas: cada parcela é contabilizada apenas quando seu due_date vence
        
        Args:
            db: Instância do banco de dados
            account_id: ObjectId da conta
            initial_balance: Saldo inicial da conta
            
        Returns:
            Saldo calculado da conta
        """
        from datetime import date as date_type
        import logging
        logger = logging.getLogger(__name__)
        
        # usar data de hoje (sem hora) para comparação segura
        today = datetime.now().date()
        today_end = datetime.combine(today, datetime.max.time())
        
        print(f"[DEBUG calc_balance] account_id: {account_id}, initial_balance: {initial_balance}, today: {today}, today_end: {today_end}")
        logger.debug(f"[calc_balance] account_id: {account_id}, initial_balance: {initial_balance}, today: {today}, today_end: {today_end}")
        
        # Buscar todas as transaction_entries da conta com due_date <= hoje (fim do dia)
        cursor = db.transaction_entries.find({
            "account_id": account_id,
            "due_date": {"$lte": today_end},
            "status": "completed"
        })
        
        balance = initial_balance
        count = 0
        async for entry in cursor:
            count += 1
            amount = entry.get("amount", 0)
            flow_type = entry.get("flow_type")
            due_date = entry.get("due_date")
            
            print(f"[DEBUG calc_balance] Entry {count}: amount={amount}, flow_type={flow_type}, due_date={due_date}")
            logger.debug(f"[calc_balance] Entry {count}: amount={amount}, flow_type={flow_type}, due_date={due_date}")
            
            if not flow_type:
                # tentamos obter do documento pai da transação, caso exista
                try:
                    tid = entry.get("transaction_id")
                    if tid:
                        txn = await db.transactions.find_one({"_id": tid})
                        if txn:
                            flow_type = txn.get("flow_type")
                            print(f"[DEBUG calc_balance] flow_type from txn: {flow_type}")
                            logger.debug(f"[calc_balance] flow_type from txn: {flow_type}")
                except Exception as e:
                    print(f"[DEBUG calc_balance] Error fetching txn: {str(e)}")
                    logger.error(f"[calc_balance] Error fetching txn: {str(e)}")
                    flow_type = None
            
            # padrão para entradas antigas sem info: consideramos income se valor positivo e
            # não houver flow_type (protege contra saldo negativo inesperado)
            if not flow_type:
                flow_type = "income" if amount >= 0 else "expense"
                print(f"[DEBUG calc_balance] flow_type set by default: {flow_type}")
                logger.debug(f"[calc_balance] flow_type set by default: {flow_type}")
                # podemos persistir o ajuste para evitar repetir no futuro
                try:
                    await db.transaction_entries.update_one(
                        {"_id": entry.get("_id")},
                        {"$set": {"flow_type": flow_type}}
                    )
                except Exception:
                    pass

            # Income aumenta o saldo, expense diminui
            if flow_type == "income":
                balance += amount
            else:  # expense
                balance -= amount
            
            print(f"[DEBUG calc_balance] Balance now: {balance}")
            logger.debug(f"[calc_balance] Balance now: {balance}")
        
        print(f"[DEBUG calc_balance] Total entries processed: {count}, final balance: {balance}")
        logger.debug(f"[calc_balance] Total entries processed: {count}, final balance: {balance}")
        return balance
