from fastapi import FastAPI
from database import engine,Base
from app.auth import models
from app.auth.routes  import router as auth_router
Base.metadata.create_all(bind=engine)

app=FastAPI()
app.include_router(auth_router)
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