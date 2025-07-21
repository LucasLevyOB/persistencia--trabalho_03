from typing import List
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.models.Motorista import Motorista
from src.models.Veiculo import Veiculo
from src.schemas.FilterParameter import FilterParameter
from src.schemas.BaseResponse import BaseResponse
from src.schemas.PagedBaseResponse import PagedBaseResponse
from src.schemas.SortParameter import SortParameter
from src.validations.validateFilter import validate_filter
from src.validations.validateSortBy import validate_sort_by

router = APIRouter(tags=["Veiculos"])

@router.post("/veiculos")
async def create_veiculo_endpoint(motorista_id: str, placa: str, modelo: str, ano: int, cor: str):
  try:
    motorista = await Motorista.get(motorista_id)

    if not motorista:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Motorista não encontrado")
    
    veiculo = Veiculo(
      placa=placa,
      modelo=modelo,
      ano=ano,
      cor=cor,
      motorista=motorista_id
    )

    inserted = await veiculo.insert()

    if not inserted:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao inserir veiculo no banco de dados")
    
    return JSONResponse(
      status_code=201,
      content=BaseResponse[str](success=True, message="Veiculo criado com sucesso", data=inserted.id).model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao criar veiculo: {str(e)}").model_dump()
    )

@router.get("/veiculos/count")
async def count_veiculos_endpoint():
  try:
    total = await Veiculo.find_all().count()
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse[int](success=True, message="Contagem total de veiculos", data=total).model_dump()
    )
  except HTTPException as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao contar veiculos: {str(e)}").model_dump()
    )

@router.get("/veiculos/{veiculo_id}")
async def get_veiculo_endpoint(veiculo_id: str):
  try:
    veiculo = await Veiculo.get(document_id=veiculo_id, fetch_links=True)

    if not veiculo:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veiculo não encontrado")
    
    return JSONResponse(
      status_code=200,
      content=jsonable_encoder(BaseResponse[Veiculo](success=True, message="Veiculo encontrado", data=veiculo).model_dump())
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao buscar veiculo: {str(e)}").model_dump()
    )

@router.put("/veiculos/{veiculo_id}")
async def update_veiculo_endpoint(veiculo_id: str = None, modelo: str = None, ano: int = None, cor: str = None):
  try:
    veiculo = await Veiculo.get(veiculo_id)

    if not veiculo:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veiculo não encontrado")
    
    if modelo:
      veiculo.modelo = modelo
    if ano:
      veiculo.ano = ano
    if cor:
      veiculo.cor = cor

    updated = await veiculo.save()

    if not updated:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar veiculo")
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse(success=True, message="Veiculo atualizado com sucesso").model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao atualizar veiculo: {str(e)}").model_dump()
    )

@router.delete("/veiculos/{veiculo_id}")
async def delete_veiculo_endpoint(veiculo_id: str):
  try:
    veiculo = await Veiculo.get(veiculo_id)

    if not veiculo:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veiculo não encontrado")
    
    deleted = await veiculo.delete()

    if not deleted:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao deletar veiculo")
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse(success=True, message="Veiculo deletado com sucesso").model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao deletar veiculo: {str(e)}").model_dump()
    )

@router.post("/veiculos/filter")
async def filter_veiculos_endpoint(filter: FilterParameter = {}, sort_by: SortParameter = None, page: int = 1, page_size: int = 3):
  try:
    validate_sort_by(Veiculo, sort_by)
    
    coluna, direcao = sort_by if sort_by else (None, None)
    
    validate_filter(Veiculo, filter)

    parsed_direcao = '+' if direcao == "asc" else '-'
    parsed_sort_by = f"{parsed_direcao}{coluna}"

    skip = (page - 1) * page_size
    veiculos = await Veiculo.find(filter, fetch_links=True).sort(parsed_sort_by).skip(skip).limit(page_size).to_list()
    total_records = len(veiculos)
    total_pages = (total_records + page_size - 1) // page_size
    
    return JSONResponse(
      status_code=200,
      content=jsonable_encoder(PagedBaseResponse[Veiculo](
        total_records=total_records,
        total_pages=total_pages,
        current_page=page,
        data=veiculos
      ).model_dump())
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao filtrar veiculos: {str(e)}").model_dump()
    )