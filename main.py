from fastapi import FastAPI
from src.database.init_beanie import init_beanie
from src.routes.motorista import router as motorista_router
from src.routes.veiculo import router as veiculo_router
from src.routes.passageiro import router as passageiro_router
from src.routes.localizacao import router as localizacao_router
from src.routes.viagem import router as viagem_router

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_beanie()

@app.get("/")
def home():
    return {"msg": "Olá, mundo!"}

app.include_router(passageiro_router)
app.include_router(motorista_router)
app.include_router(veiculo_router)
app.include_router(localizacao_router)
app.include_router(viagem_router)
