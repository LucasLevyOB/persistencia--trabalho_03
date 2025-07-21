# Persistência - Trabalho 3

Projeto de API REST em Python utilizando FastAPI, Beanie ODM e MongoDB para gerenciamento de motoristas, veículos, passageiros, localizações e viagens.

## Tecnologias

- Python 3.10+
- FastAPI
- Beanie (ODM para MongoDB)
- MongoDB

## Estrutura

```
src/
  database/
    init_beanie.py
    database.py
  models/
    Motorista.py
    Veiculo.py
    Passageiro.py
    Localizacao.py
    Viagem.py
  routes/
    motorista.py
    veiculo.py
    passageiro.py
    localizacao.py
    viagem.py
  schemas/
    BaseResponse.py
    FilterParameter.py
    PagedBaseResponse.py
    SortParameter.py
  validations/
    validateFilter.py
    validateSortBy.py
main.py
```

## Como rodar

1. **Inicie o MongoDB**  
   ```sh
   sudo systemctl start mongod
   ```

2. **Instale as dependências**  
   ```sh
   pip install -r requirements.txt
   ```

3. **Execute o projeto**  
   ```sh
   uvicorn main:app --reload
   ```

## Endpoints principais

- `/motoristas` - CRUD de motoristas
- `/veiculos` - CRUD de veículos
- `/passageiros` - CRUD de passageiros
- `/localizacoes` - CRUD de localizações
- `/viagens` - CRUD de viagens
- Consultas complexas envolvendo múltiplas entidades

## Observações

- O Beanie é inicializado no evento de startup do FastAPI.
- As respostas da API são padronizadas usando schemas Pydantic.
- Para consultas complexas, utilize os endpoints específicos em `routes/viagem.py`.

## Autores

- Lucas