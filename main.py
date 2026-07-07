from fastapi import FastAPI

app=FastAPI()

@app.get("/")
def read_root():
    return {"message":"Pizza platform backend is running"}