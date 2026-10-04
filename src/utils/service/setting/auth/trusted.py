from pydantic import BaseModel, Field
from typing import Optional


class TrustedAuthSetting(BaseModel):
    username: str = Field(
        default=None,
        description="Имя пользователя",
    )

    private_key: Optional[str] = Field(
        default=None,
        description="Ключ для входа. На сервере должен лежать открытый ключ",
    )

    private_key_password: Optional[str] = Field(
        default=None, description="Пароль от ключа"
    )


class TrustedSetting(BaseModel):

    auth: Optional[TrustedAuthSetting] = Field(
        default=None,
        description="Настройки аутентификации",
    )

    enable: bool = Field(
        default=False,
        description="Доступна ли аутентификация через доверенные узлы",
    )

    white_list: Optional[list[bool]] = Field(
        default=None,
        description="Список разрешенных хостов",
    )