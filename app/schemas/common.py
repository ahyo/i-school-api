from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class PesanResponse(BaseModel):
    pesan: str


class StandardResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None
    statusCode: int
