# services/date_utils.py
from datetime import date
from dateutil.relativedelta import relativedelta

def calculate_due_date(purchase_date: date, closing_day: int, due_day: int) -> date:
    if purchase_date.day > closing_day:
        base_date = purchase_date + relativedelta(months=1)
    else:
        base_date = purchase_date

    return date(base_date.year, base_date.month, due_day)

def competence_month(d: date) -> str:
    return f"{d.year}-{str(d.month).zfill(2)}"
