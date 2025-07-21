from datetime import date
import uuid
from beanie import Document, Indexed
from pydantic import Field

class Motorista(Document):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
  cpf: Indexed(str)
  nome: str
  email: Indexed(str)
  senha: str
  criado_em: date = Field(default_factory=date.today)

  class Settings:
    name = "motoristas"
