import uuid
from beanie import Document, Indexed, Link
from pydantic import Field


from src.models.Motorista import Motorista

class Veiculo(Document):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
  placa: Indexed(str)
  modelo: str
  ano: int
  cor: str
  motorista: Link[Motorista]

  class Settings:
    name = "veiculos"
