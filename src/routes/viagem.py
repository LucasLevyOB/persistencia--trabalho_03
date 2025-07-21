from datetime import date
from typing import List
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.models.Localizacao import Localizacao
from src.models.Passageiro import Passageiro
from src.models.Motorista import Motorista
from src.models.Viagem import Status, Viagem
from src.schemas.FilterParameter import FilterParameter
from src.schemas.BaseResponse import BaseResponse
from src.schemas.PagedBaseResponse import PagedBaseResponse
from src.schemas.SortParameter import SortParameter
from src.validations.validateFilter import validate_filter
from src.validations.validateSortBy import validate_sort_by

router = APIRouter(tags=["Viagens"])

@router.post("/viagens")
async def create_viagem_endpoint(motorista_id: str, passageiro_id: str, localizacao_inicial_id: str, localizacao_final_id: str):
  try:
    motorista = await Motorista.get(motorista_id)

    if not motorista:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Motorista não encontrado")
    
    passageiro = await Passageiro.get(passageiro_id)

    if not passageiro:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passageiro não encontrado")
    
    localizacao_inicial = await Localizacao.get(localizacao_inicial_id)

    if not localizacao_inicial:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Localização inicial não encontrada")
    
    localizacao_final = await Localizacao.get(localizacao_final_id)

    if not localizacao_final:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Localização final não encontrada")
    
    veiculo = Viagem(
      motorista=motorista_id,
      passageiro=passageiro_id,
      localizacao_inicial=localizacao_inicial_id,
      localizacao_final=localizacao_final_id
    )

    inserted = await veiculo.insert()

    if not inserted:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao inserir viagem no banco de dados")
    
    return JSONResponse(
      status_code=201,
      content=BaseResponse[str](success=True, message="Viagem criada com sucesso", data=inserted.id).model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao criar viagem: {str(e)}").model_dump()
    )

@router.get("/viagens/count")
async def count_viagens_endpoint():
  try:
    total = await Viagem.find_all().count()
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse[int](success=True, message="Contagem total de viagens", data=total).model_dump()
    )
  except HTTPException as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao contar viagens: {str(e)}").model_dump()
    )

@router.get("/viagens/{viagem_id}")
async def get_viagem_endpoint(viagem_id: str):
  try:
    viagem = await Viagem.get(document_id=viagem_id, fetch_links=True)

    if not viagem:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Viagem não encontrada")
    
    return JSONResponse(
      status_code=200,
      content=jsonable_encoder(BaseResponse[Viagem](success=True, message="Viagem encontrada", data=viagem).model_dump())
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao buscar viagem: {str(e)}").model_dump()
    )

@router.get("/viagens/ano/{viagem_ano}")
async def get_viagem_ano_endpoint(viagem_ano: int):
  try:
    print(viagem_ano)
    filter = {
      "criado_em": {
        "$gte": date(int(viagem_ano), 1, 1),
        "$lt": date(int(viagem_ano) + 1, 1, 1)
      }
    }

    viagens = Viagem.find(filter).aggregate(
      [
        {
          "$group": {
            "_id": "$criado_em",
            "total": {"$sum": 1}
          }
        },
        {
          "$project": {
            "ano": {"$year": "$_id"},
            "total": 1
          }
        }
      ]
    )

    viagens_list = await viagens.to_list()

    if not viagens_list:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma viagem encontrada para o ano especificado")
    
    return JSONResponse(
      status_code=200,
      content=jsonable_encoder(BaseResponse[List[dict]](success=True, message="Viagens encontradas", data=viagens_list).model_dump())
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao buscar viagem: {str(e)}").model_dump()
    )

@router.get("/viagens/ponto_partida/count")
async def get_viagens_ponto_partida_count_endpoint():
  try:
    pipeline = [
      {
        "$addFields": {
          "localizacao_id": "$localizacao_inicial.$id"
        }
      },
      {
        "$lookup": {
          "from": "localizacoes",
          "localField": "localizacao_id",
          "foreignField": "_id",
          "as": "ponto_partida_info"
        }
      },
      {
        "$unwind": "$ponto_partida_info"
      },
      {
        "$group": {
          "_id": "$ponto_partida_info.cidade",
          "total": {"$sum": 1}
        }
      },
      {
        "$project": {
          "_id": 0,
          "ponto_partida": "$_id",
          "total": "$total"
        }
      }
    ]
    
    viagens_aggregate = Viagem.aggregate(pipeline)
    viagens_list = await viagens_aggregate.to_list()
    print(viagens_list)

    if not viagens_list:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma viagem encontrada")
    
    return JSONResponse(
      status_code=200,
      content=jsonable_encoder(BaseResponse[List[dict]](success=True, message="Viagens por ponto de partida encontradas", data=viagens_list).model_dump())
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao buscar viagens por ponto de partida: {str(e)}").model_dump()
    )

@router.put("/viagens/{viagem_id}")
async def update_viagem_endpoint(viagem_id: str, status: int):
  try:
    viagem = await Viagem.get(viagem_id)

    if not viagem:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Viagem não encontrado")
    
    viagem.status = Status(status)

    updated = await viagem.save()

    if not updated:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao atualizar viagem")
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse(success=True, message="Viagem atualizado com sucesso").model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao atualizar veiculo: {str(e)}").model_dump()
    )

@router.delete("/viagens/{viagem_id}")
async def delete_viagem_endpoint(viagem_id: str):
  try:
    viagem = await Viagem.get(viagem_id)

    if not viagem:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Viagem não encontrada")
    
    deleted = await viagem.delete()

    if not deleted:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao deletar viagem")
    
    return JSONResponse(
      status_code=200,
      content=BaseResponse(success=True, message="Viagem deletada com sucesso").model_dump()
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao deletar viagem: {str(e)}").model_dump()
    )

@router.post("/viagens/filter")
async def filter_viagem_endpoint(filter: FilterParameter = {}, sort_by: SortParameter = None, page: int = 1, page_size: int = 3):
  try:
    validate_sort_by(Viagem, sort_by)
    
    coluna, direcao = sort_by if sort_by else (None, None)
    
    validate_filter(Viagem, filter)

    parsed_direcao = '+' if direcao == "asc" else '-'
    parsed_sort_by = f"{parsed_direcao}{coluna}"

    skip = (page - 1) * page_size
    viagens = await Viagem.find(filter, fetch_links=True).sort(parsed_sort_by).skip(skip).limit(page_size).to_list()
    total_records = len(viagens)
    total_pages = (total_records + page_size - 1) // page_size
    
    return JSONResponse(
      status_code=200,
      content=jsonable_encoder(PagedBaseResponse[Viagem](
        total_records=total_records,
        total_pages=total_pages,
        current_page=page,
        data=viagens
      ).model_dump())
    )
  
  except Exception as e:
    return JSONResponse(
      status_code=e.status_code if isinstance(e, HTTPException) else 500,
      content=BaseResponse(success=False, message=f"Erro ao filtrar viagens: {str(e)}").model_dump()
    )