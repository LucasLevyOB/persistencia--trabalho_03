from datetime import date
import uuid
from beanie import Document, Indexed
from pydantic import Field

class Localizacao(Document):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
  cidade: str
  rua: str
  numero: int
  latitude: float
  longitude: float

  class Settings:
    name = "localizacoes"
