from typing import Generic, List, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class PagedBaseResponse(BaseModel, Generic[T]):
  total_records: int
  total_pages: int
  current_page: int
  data: List[T]