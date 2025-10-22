from pydantic import BaseModel


class PesanResponse(BaseModel):
    pesan: str
