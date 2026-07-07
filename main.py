from fastapi import FastAPI
from database import engine,Base
from app.auth import models
Base.metadata.create_all(bind=engine)

app=FastAPI()

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