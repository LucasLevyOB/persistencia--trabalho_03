from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.models.Passageiro import Passageiro
from src.schemas.FilterParameter import FilterParameter
from src.schemas.BaseResponse import BaseResponse
from src.schemas.PagedBaseResponse import PagedBaseResponse
from src.schemas.SortParameter import SortParameter
from src.validations.validateFilter import validate_filter
from src.validations.validateSortBy import validate_sort_by


router = APIRouter(tags=["Passageiros"])

@router.post("/passageiros")
async def create_passageiro_endpoint(cpf: str, nome: str, email: str, senha: str):
  try:
    passageiro = Passageiro(cpf=cpf, nome=nome, email=email, senha=senha)

    inserted = await passageiro.insert()

    if not inserted:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao inserir passageiro no banco de dados")
    
    return JSONResponse(
      status_code=201,
      content=BaseResponse[str](success=True, message="Passageiro criado com sucesso", data=inserted.id).model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao criar passageiro: {str(e)}").model_dump()
    )

@router.get("/passageiros/count")
async def count_passageiros_endpoint():
  try:
    total = await Passageiro.find_all().count()
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse[int](success=True, message="Contagem total de passageiros", data=total).model_dump()
    )
  except HTTPException as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao contar passageiros: {str(e)}").model_dump()
    )

@router.get("/passageiros/{motorista_id}")
async def get_passageiro_endpoint(motorista_id: str):
  try:
    passageiro = await Passageiro.get(motorista_id)

    if not passageiro:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passageiro não encontrado")
    
    return JSONResponse(
      status_code=200,
      content=jsonable_encoder(BaseResponse[Passageiro](success=True, message="Passageiro encontrado com sucesso", data=passageiro).model_dump())
    )
  except HTTPException as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao buscar passageiro: {str(e)}").model_dump()
    )

@router.put("/passageiros/{motorista_id}")
async def update_passageiro_endpoint(motorista_id: str, nome: str = None, email: str = None, senha: str = None):
  try:
    passageiro = await Passageiro.get(motorista_id)

    if not passageiro:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passageiro não encontrado")
    
    if nome:
      passageiro.nome = nome
    if email:
      passageiro.email = email
    if senha:
      passageiro.senha = senha

    updated = await passageiro.save()

    if not updated:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar passageiro")
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse(success=True, message="Passageiro atualizado com sucesso").model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao atualizar passageiro: {str(e)}").model_dump()
    )

@router.delete("/passageiros/{motorista_id}")
async def delete_passageiro_endpoint(motorista_id: str):
  try:
    passageiro = await Passageiro.get(motorista_id)

    if not passageiro:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passageiro não encontrado")
    
    deleted = await passageiro.delete()

    if not deleted:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao deletar passageiro")
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse(success=True, message="Passageiro deletado com sucesso").model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao deletar passageiro: {str(e)}").model_dump()
    )

@router.post("/passageiros/filter")
async def filter_passageiros_endpoint(filter: FilterParameter = {}, sort_by: SortParameter = None, page: int = 1, page_size: int = 3):
  try:
    validate_sort_by(Passageiro, sort_by)
    
    coluna, direcao = sort_by if sort_by else (None, None)
    
    validate_filter(Passageiro, filter)

    parsed_direcao = '+' if direcao == "asc" else '-'
    parsed_sort_by = f"{parsed_direcao}{coluna}"

    skip = (page - 1) * page_size
    passageiros = await Passageiro.find(filter).sort(parsed_sort_by).skip(skip).limit(page_size).to_list()
    total_records = len(passageiros)
    total_pages = (total_records + page_size - 1) // page_size
    
    return JSONResponse(
      status_code=200,
      content=jsonable_encoder(PagedBaseResponse[Passageiro](
        total_records=total_records,
        total_pages=total_pages,
        current_page=page,
        data=passageiros
      ).model_dump())
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao filtrar passageiros: {str(e)}").model_dump()
    )