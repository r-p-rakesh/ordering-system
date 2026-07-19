from fastapi import FastAPI
from database import engine,Base
from app.auth import models
from app.auth.routes  import router as auth_router
from app.restaurants import models as restaurant_models
from app.menu import models as menu_models
from app.menu.routes import router as menu_router
from app.orders.routes import router as order_router
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app=FastAPI()
import os

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(menu_router)
app.include_router(order_router)

@app.get("/")
def read_root():
    return {"message":"Pizza platform backend is running"}

@app.get("/dbcheck")
def db_check():
    try:
        with engine.connect() as conn:
            return {"status":"Database connected successfully"}
    except Exception as e:
        return {"status":"Connection failed", "error":str(e)}





