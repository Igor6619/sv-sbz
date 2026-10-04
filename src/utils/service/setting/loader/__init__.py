import os
import json
import pydantic

SETTING_PATH_ENV_NAME = "SERVICE_SETTING_PATH"
DEFAULT_SETTING_FILE_PATH = "../setting.service.json"
AUTO_GENERATE_CONFIG=True if os.getenv(key="AUTO_GENERATE_CONFIG", default="true").lower() in [ "true", "on" ] else False

def get_sub_setting(
    id: str,
    model: pydantic.BaseModel | None = None,
    adapter: pydantic.TypeAdapter | pydantic.BaseModel | None = None,
    default_value: any = None,
    default_path: str = DEFAULT_SETTING_FILE_PATH,
    auto_set_setting_on_error=AUTO_GENERATE_CONFIG,
) -> any:
    path = os.getenv(key=SETTING_PATH_ENV_NAME, default=default_path)

    try:
        with open(path, "rb") as f:
            json_data: dict = json.load(f)
            if id in json_data:
                result = setting_env_post_handler(json=json_data.get(id, None))

                if model is not None and result is not None:
                    return setting_env_post_handler(model.model_validate(result))
                elif adapter is not None and result is not None:
                    return setting_env_post_handler(adapter.validate_python(result))
                elif result is not None:
                    return result
    except Exception as ex:
        print(f"Ошибка чтения файла настроек секции {id} по пути {path}", ex)

    if auto_set_setting_on_error:
        try:
            set_sub_setting(
                id=id,
                value=(default_value if default_value is not None else None),
                default_path=default_path,
            )
        except Exception as ex:
            import traceback

            print(f"Error save settings: {path}\n{traceback.format_exc()}", ex)

    if default_value is not None:
        print(f"Использование настроек по умолчанию для {id}")
        return setting_env_post_handler(default_value)

    raise ValueError(f"Не удалось загрузить настроки {id} из {path}")


def set_sub_setting(
    id: str,
    value: any,
    default_path: str = DEFAULT_SETTING_FILE_PATH,
) -> any:
    path = os.getenv(key=SETTING_PATH_ENV_NAME, default=default_path)
    json_data = dict()

    if value is not None and isinstance(value, pydantic.BaseModel):
        json_data = value.model_dump()

    elif value is not None and isinstance(value, list):
        json_data = list()
        for item in value:
            if isinstance(item, pydantic.BaseModel):
                json_data.append(item.model_dump(exclude_none=True))
            else:
                json_data.append(item)

    elif value is not None and isinstance(value, dict):
        for k, v in value.items():
            if isinstance(item, pydantic.BaseModel):
                json_data[k] = item.model_dump()
            else:
                json_data[k] = v

    all_data = {}
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                all_data = json.load(f)
        except Exception:
            pass

    all_data[id] = json_data
    with open(path, "w") as f:
        json.dump(all_data, f, indent=2)

    return value


def setting_env_post_handler(json: any) -> any:
    if isinstance(json, dict):
        json = dict([(k, setting_env_post_handler(v)) for k, v in json.items()])
    elif isinstance(json, list):
        json = [setting_env_post_handler(i) for i in json]
    elif isinstance(json, str):
        if "${" in json:
            for key, value in os.environ.items():
                json = json.replace("${" + key + "}", value)
    elif json is not None and isinstance(json, pydantic.BaseModel):
        try:

            for key in json.model_fields.keys():
                try:
                    setattr(json, key, setting_env_post_handler(getattr(json, key)))
                except Exception:
                    pass
        except Exception:
            pass

    return json


__all__ = [
    "get_sub_setting",
    "set_sub_setting",
    "setting_env_post_handler",
]
