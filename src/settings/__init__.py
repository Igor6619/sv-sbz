from pydantic import BaseModel, Field
from utils.service import (
    AuthClientSetting,
    DataBaseSetting,
    CorsSetting,
    get_sub_setting,
)


class SbzSetting(BaseModel):
    """Основные настройки"""

    files_path: str = Field(
        default="${STORAGE_FILES_PATH}",
        description="Путь к хранилищу файлов",
    )

    omni_url: str = Field(
        default="${OMNI_SERVICE_URL}",
        description="url системы агентов",
    )


SETTING_AUTH: AuthClientSetting = get_sub_setting(
    "auth.client",
    model=AuthClientSetting,
    default_value=AuthClientSetting(),
    auto_set_setting_on_error=True,
)

SETTING_DB: DataBaseSetting = get_sub_setting(
    "db",
    model=DataBaseSetting,
    default_value=DataBaseSetting(),
    auto_set_setting_on_error=False,
)

SETTING_CORS: CorsSetting = get_sub_setting(
    "cors",
    model=CorsSetting,
    default_value=CorsSetting(),
    auto_set_setting_on_error=True,
)

SETTING: SbzSetting = get_sub_setting(
    "sbz",
    model=SbzSetting,
    default_value=SbzSetting(),
    auto_set_setting_on_error=True,
)

__all__ = ["SbzSetting", "SETTING", "SETTING_DB", "SETTING_AUTH", "SETTING_CORS"]
