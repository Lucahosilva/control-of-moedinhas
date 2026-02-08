from fastapi import FastAPI
from app.routes import transactions, households, categories, accounts, users, expense_splits

app = FastAPI(title="Finance Manager")

app.include_router(transactions.router)
app.include_router(households.router)
app.include_router(categories.router)
app.include_router(accounts.router)
app.include_router(users.router)
app.include_router(expense_splits.router)
