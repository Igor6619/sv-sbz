from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from ...tools import PydanticHelper


class JwtTokenCredentials(BaseModel):
    Token: Optional[str] = Field(default=None)
    ApiKey: Optional[str] = Field(default=None)


class JwtTokenQueryCredentials(BaseModel):
    token: Optional[str] = Field(default=None)
    apikey: Optional[str] = Field(default=None)


class JwtTokenCredentialsRequired(BaseModel):
    Token: Optional[str] = Field(
        ...,
    )


class TrustedNodeJwt(BaseModel, PydanticHelper.mixins.datetime("created")):
    id: str = Field(
        ...,
        description="Уникальный идентификатор",
    )

    created: datetime = Field(
        ...,
        description="Метка времни создания",
    )
