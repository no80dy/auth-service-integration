import uuid

from pydantic import BaseModel, Field


class BaseProjectModel(BaseModel):
    id: uuid.UUID = Field(..., serialization_alias='uuid')

    class Config:
        populate_by_name = True
