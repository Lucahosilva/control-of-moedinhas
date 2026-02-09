from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import transactions, cost_centers, categories, accounts, users

app = FastAPI(title="Finance Manager")

# CORS middleware: permitir requests do front-end em desenvolvimento
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(transactions.router)
app.include_router(cost_centers.router)
app.include_router(categories.router)
app.include_router(accounts.router)
app.include_router(users.router)
