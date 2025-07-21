from pyclbr import Class
from fastapi import HTTPException, status
from src.schemas.SortParameter import SortParameter


def validate_sort_by(model: Class, sort_by: SortParameter):
  coluna, direcao = sort_by if sort_by else (None, None)
  if sort_by:
    if not coluna or not direcao:
      raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Parâmetros de ordenação inválido")
    if direcao not in ["asc", "desc"]:
      raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Direção de ordenação '{direcao}' inválida. Use 'asc' ou 'desc'.")
    if not hasattr(model, coluna):
      raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Coluna '{coluna}' não existe no modelo")