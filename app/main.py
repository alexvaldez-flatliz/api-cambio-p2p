from fastapi import FastAPI
from .database import engine
from . import models
from .routers import router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kambio P2P Full")

app.include_router(router)

@app.get("/")
def root():
    return {"ok": True}