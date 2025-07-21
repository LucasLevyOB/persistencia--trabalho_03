from datetime import date
import uuid
from enum import Enum, auto
from beanie import Document, Indexed, Link

from pydantic import Field


from src.models.Motorista import Motorista
from src.models.Passageiro import Passageiro
from src.models.Localizacao import Localizacao

class Status(Enum):
    CRIADA = auto()
    ESPERANDO = auto()
    ACEITA = auto()
    INICIADA = auto()
    FINALIZADA = auto()
    CANCELADA_MOTORISTA = auto()
    CANCELADA_PASSAGEIRO = auto()

class Viagem(Document):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
  status: Status = Field(sa_column_kwargs={"nullable": False}, default=Status.CRIADA)
  motorista: Link[Motorista]
  passageiro: Link[Passageiro]
  localizacao_inicial: Link[Localizacao]
  localizacao_final: Link[Localizacao]
  criado_em: date = Field(default_factory=date.today)

  class Settings:
    name = "viagens"
