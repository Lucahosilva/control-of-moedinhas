# services/transaction_service.py
from datetime import date
from typing import List
from dateutil.relativedelta import relativedelta

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
                    amount=transaction.amount,
                    competence_month=competence_month(due),
                    due_date=due,
                    payment_method=pm.type,
                    account_id=transaction.account_id,
                    category_id=transaction.category_id,
                    household_id=transaction.household_id,
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
                    amount=transaction.amount,
                    competence_month=competence_month(due),
                    due_date=due,
                    payment_method=pm.type,
                    account_id=transaction.account_id,
                    category_id=transaction.category_id,
                    household_id=transaction.household_id,
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
