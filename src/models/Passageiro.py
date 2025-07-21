from datetime import date
from typing import Annotated
import uuid
from beanie import Document, Indexed
from pydantic import Field

class Passageiro(Document):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
  # cpf: Annotated[str, Indexed(unique=True)]
  cpf: Indexed(str)
  nome: str
  # email: Annotated[str, Indexed(unique=True)]
  email: Indexed(str)
  senha: str
  criado_em: date = Field(default_factory=date.today)

  class Settings:
    name = "passageiros"
