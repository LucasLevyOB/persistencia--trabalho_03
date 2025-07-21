from pyclbr import Class
from fastapi import HTTPException, status
from src.schemas.FilterParameter import FilterParameter


def validate_filter(model: Class, filter: FilterParameter):
  if filter:
    if not isinstance(filter, dict):
      raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Filtro deve ser um dicionário")
    for key in filter:
      # if not hasattr(model, key):
      #   raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Filtro inválido: '{key}' não é um campo válido para a tabela")
      if not isinstance(filter[key], dict):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Filtro inválido: '{key}' deve ser um dicionário")
      for query_filter in filter[key]:
        if query_filter not in ["$eq", "$ne", "$gt", "$lt", "$gte", "$lte", "$in", "$nin", "$regex"]:
          raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Filtro inválido: '{query_filter}' não é um operador válido")
        if not isinstance(filter[key][query_filter], (str, int, float, list)):
          raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Filtro inválido: valor para '{key}' deve ser uma string, número ou lista")