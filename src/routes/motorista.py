from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.models.Motorista import Motorista
from src.schemas.FilterParameter import FilterParameter
from src.schemas.BaseResponse import BaseResponse
from src.schemas.PagedBaseResponse import PagedBaseResponse
from src.schemas.SortParameter import SortParameter
from src.validations.validateFilter import validate_filter
from src.validations.validateSortBy import validate_sort_by


router = APIRouter(tags=["Motoristas"])

@router.post("/motoristas")
async def create_motorista_endpoint(cpf: str, nome: str, email: str, senha: str):
  try:
    motorista = Motorista(cpf=cpf, nome=nome, email=email, senha=senha)

    inserted = await motorista.insert()

    if not inserted:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao inserir motorista no banco de dados")
    
    return JSONResponse(
      status_code=201,
      content=BaseResponse[str](success=True, message="Motorista criado com sucesso", data=inserted.id).model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao criar motorista: {str(e)}").model_dump()
    )

@router.get("/motoristas/count")
async def count_motoristas_endpoint():
  try:
    total = await Motorista.find_all().count()
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse[int](success=True, message="Contagem total de motoristas", data=total).model_dump()
    )
  except HTTPException as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao contar motoristas: {str(e)}").model_dump()
    )

@router.get("/motoristas/{motorista_id}")
async def get_motorista_endpoint(motorista_id: str):
  try:
    motorista = await Motorista.get(motorista_id)

    if not motorista:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Motorista não encontrado")
    
    return JSONResponse(
      status_code=200,
      content=jsonable_encoder(BaseResponse[Motorista](success=True, message="Motorista encontrado com sucesso", data=motorista).model_dump())
    )
  except HTTPException as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao buscar motorista: {str(e)}").model_dump()
    )

@router.put("/motoristas/{motorista_id}")
async def update_motorista_endpoint(motorista_id: str, nome: str = None, email: str = None, senha: str = None):
  try:
    motorista = await Motorista.get(motorista_id)

    if not motorista:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Motorista não encontrado")
    
    if nome:
      motorista.nome = nome
    if email:
      motorista.email = email
    if senha:
      motorista.senha = senha

    updated = await motorista.save()

    if not updated:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar motorista")
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse(success=True, message="Motorista atualizado com sucesso").model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao atualizar motorista: {str(e)}").model_dump()
    )

@router.delete("/motoristas/{motorista_id}")
async def delete_motorista_endpoint(motorista_id: str):
  try:
    motorista = await Motorista.get(motorista_id)

    if not motorista:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Motorista não encontrado")
    
    deleted = await motorista.delete()

    if not deleted:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao deletar motorista")
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse(success=True, message="Motorista deletado com sucesso").model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao deletar motorista: {str(e)}").model_dump()
    )

@router.post("/motoristas/filter")
async def filter_motoristas_endpoint(filter: FilterParameter = {}, sort_by: SortParameter = None, page: int = 1, page_size: int = 3):
  try:
    validate_sort_by(Motorista, sort_by)
    
    coluna, direcao = sort_by if sort_by else (None, None)
    
    validate_filter(Motorista, filter)

    parsed_direcao = '+' if direcao == "asc" else '-'
    parsed_sort_by = f"{parsed_direcao}{coluna}"

    skip = (page - 1) * page_size
    motoristas = await Motorista.find(filter).sort(parsed_sort_by).skip(skip).limit(page_size).to_list()
    total_records = len(motoristas)
    total_pages = (total_records + page_size - 1) // page_size
    
    return JSONResponse(
      status_code=200,
      content=jsonable_encoder(PagedBaseResponse[Motorista](
        total_records=total_records,
        total_pages=total_pages,
        current_page=page,
        data=motoristas
      ).model_dump())
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao filtrar motoristas: {str(e)}").model_dump()
    )