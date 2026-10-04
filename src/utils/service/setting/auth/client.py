from typing import Optional
from pydantic import BaseModel, Field
from .trusted import TrustedSetting


class AuthClientSetting(BaseModel):
    url: str = Field(
        default="${AUTH_SERVICE_URL}",
        description="URL сервера аутентификации",
    )
    version: str = Field(
        default="1",
        description="Версия аутентификаци",
    )
    public_key: Optional[str] = Field(
        default=None,
        description="Открытый ключ для проверки подписи сервера. Если None, то автоматически скачивается с сервера",
    )
    min_jwt_balance_sec: int = Field(
        default=5 * 60,  # 5 min,
        description="Минимальное оставшеся время жизни токена, необходимое для запуска обновления",
    )
    trusted: TrustedSetting = Field(
        default_factory=TrustedSetting,
        description="Настройки безопасного межсервисного обмена",
    )
