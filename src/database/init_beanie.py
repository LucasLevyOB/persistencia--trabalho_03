from beanie import init_beanie as beanie_init_beanie
from src.database.database import db
from src.models.Passageiro import Passageiro
from src.models.Motorista import Motorista
from src.models.Veiculo import Veiculo
from src.models.Localizacao import Localizacao
from src.models.Viagem import Viagem


async def init_beanie():
  await beanie_init_beanie(database=db, document_models=[Motorista, Veiculo, Passageiro, Localizacao, Viagem])