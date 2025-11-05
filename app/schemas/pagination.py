from math import ceil
from typing import Generic, TypeVar, Sequence
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class PaginatedResponse(GenericModel, Generic[T]):
    items: Sequence[T]
    meta: PaginationMeta
