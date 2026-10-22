from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_database
from auth import router as auth_router
from products import router as products_router
from orders import router as orders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="Café & Food API",
    description="API de gestion des clients, produits et commandes",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(auth_router, tags=["Authentification et clients"])
app.include_router(products_router, tags=["Produits"])
app.include_router(orders_router, tags=["Commandes"])


@app.get("/")
def home():
    return {
        "message": "Bienvenue sur l'API Café & Food",
        "status": "running",
        "documentation": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}