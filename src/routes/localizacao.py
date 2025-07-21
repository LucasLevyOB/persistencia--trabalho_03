from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.models.Localizacao import Localizacao
from src.schemas.FilterParameter import FilterParameter
from src.schemas.BaseResponse import BaseResponse
from src.schemas.PagedBaseResponse import PagedBaseResponse
from src.schemas.SortParameter import SortParameter
from src.validations.validateFilter import validate_filter
from src.validations.validateSortBy import validate_sort_by


router = APIRouter(tags=["Localizacoes"])

@router.post("/localizacoes")
async def create_localizacao_endpoint(cidade: str, rua: str, numero: int, latitude: float, longitude: float):
  try:
    localizacao = Localizacao(
      cidade=cidade,
      rua=rua,
      numero=numero,
      latitude=latitude,
      longitude=longitude
    )

    inserted = await localizacao.insert()

    if not inserted:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao inserir localizacao no banco de dados")
    
    return JSONResponse(
      status_code=201,
      content=BaseResponse[str](success=True, message="Localizacao criado com sucesso", data=inserted.id).model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao criar localizacao: {str(e)}").model_dump()
    )

@router.get("/localizacoes/count")
async def count_localizacoes_endpoint():
  try:
    total = await Localizacao.find_all().count()
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse[int](success=True, message="Contagem total de localizacoes", data=total).model_dump()
    )
  except HTTPException as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao contar localizacoes: {str(e)}").model_dump()
    )

@router.get("/localizacoes/{localizacao_id}")
async def get_localizacao_endpoint(localizacao_id: str):
  try:
    localizacao = await Localizacao.get(localizacao_id)

    if not localizacao:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Localizacao não encontrado")
    
    return JSONResponse(
      status_code=200,
      content=jsonable_encoder(BaseResponse[Localizacao](success=True, message="Localizacao encontrado com sucesso", data=localizacao).model_dump())
    )
  except HTTPException as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao buscar localizacao: {str(e)}").model_dump()
    )

@router.put("/localizacoes/{localizacao_id}")
async def update_localizacao_endpoint(localizacao_id: str, cidade: str = None, rua: str = None, numero: int = None, latitude: float = None, longitude: float = None):
  try:
    localizacao = await Localizacao.get(localizacao_id)

    if not localizacao:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Localizacao não encontrado")
    
    if cidade:
      localizacao.cidade = cidade
    if rua:
      localizacao.rua = rua
    if numero is not None:
      localizacao.numero = numero
    if latitude is not None:
      localizacao.latitude = latitude
    if longitude is not None:
      localizacao.longitude = longitude

    updated = await localizacao.save()

    if not updated:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar localizacao")
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse(success=True, message="Localizacao atualizado com sucesso").model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao atualizar localizacao: {str(e)}").model_dump()
    )

@router.delete("/localizacoes/{localizacao_id}")
async def delete_localizacao_endpoint(localizacao_id: str):
  try:
    localizacao = await Localizacao.get(localizacao_id)

    if not localizacao:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Localizacao não encontrado")
    
    deleted = await localizacao.delete()

    if not deleted:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao deletar localizacao")
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse(success=True, message="Localizacao deletado com sucesso").model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao deletar localizacao: {str(e)}").model_dump()
    )

@router.post("/localizacoes/filter")
async def filter_localizacoes_endpoint(filter: FilterParameter = {}, sort_by: SortParameter = None, page: int = 1, page_size: int = 3):
  try:
    validate_sort_by(Localizacao, sort_by)
    
    coluna, direcao = sort_by if sort_by else (None, None)
    
    validate_filter(Localizacao, filter)

    parsed_direcao = '+' if direcao == "asc" else '-'
    parsed_sort_by = f"{parsed_direcao}{coluna}"

    skip = (page - 1) * page_size
    localizacoes = await Localizacao.find(filter).sort(parsed_sort_by).skip(skip).limit(page_size).to_list()
    total_records = len(localizacoes)
    total_pages = (total_records + page_size - 1) // page_size
    
    return JSONResponse(
      status_code=200,
      content=jsonable_encoder(PagedBaseResponse[Localizacao](
        total_records=total_records,
        total_pages=total_pages,
        current_page=page,
        data=localizacoes
      ).model_dump())
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao filtrar localizacoes: {str(e)}").model_dump()
    )