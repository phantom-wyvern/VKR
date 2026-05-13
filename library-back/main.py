# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine
from routes import auth
from routes import admin
from routes import book
from routes import inventory
from routes import landing
from routes import loan
from routes import reports

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Подключение к БД установлено")
    yield
    # Shutdown
    await engine.dispose()
    print("Соединение с БД закрыто")

app = FastAPI(
    title="Library Management System API",
    description="Backend for the Library Information System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(book.router)
app.include_router(inventory.router)
app.include_router(landing.router)
app.include_router(loan.router)
app.include_router(reports.router)

@app.get("/")
async def root():
    return {"message": "Library API is running!"}