import functools
from enum import Enum
from uuid import UUID
import datetime as pydatetime
from typing import Union, Optional, Mapping, Sequence, Callable
from pydantic import BaseModel, field_validator, field_serializer
from pydantic.fields import ModelPrivateAttr, PrivateAttr

DEFAULT_TIME_FORMAT = "%H:%M:%S"
DEFAULT_DATE_FORMAT = "%d.%m.%Y"
DEFAULT_DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"
DEFAULT_TRUE_LIST=['true', 'on', '1']

class PydanticHelper:
    """Помошник работы с моделями Pydantic"""

    class validators:
        """Валидаторы"""
        
        @classmethod
        def bool(
            cls,
            value: Union[str, int, bool, None],
            true_list = DEFAULT_TRUE_LIST
        ) -> Union[bool, None]:
            if value is not None:
                if isinstance(value, str):
                    if value.strip().lower() in true_list:
                        return True
                    else: 
                        return False
                if isinstance(value, int) or isinstance(value, float): 
                    return value > 0
                
                return value
            return value

        @classmethod
        def uuid(
            cls,
            value: Union[str, UUID, None],
        ) -> Union[str, UUID, None]:
            if value is not None:
                if isinstance(value, str):
                    if len(value) > 0:
                        return UUID(value)
                    return None
            return value

        @classmethod
        def uuid_list(
            cls,
            value: Union[str, UUID, dict, object, list[Union[str, UUID, object, dict]]],
        ) -> Union[list[UUID], None]:
            # None
            if value is None:
                return value

            # UUID
            if isinstance(value, UUID):
                value = [value]

            # FROM STR
            elif isinstance(value, str):
                value = value.strip()
                if len(value) > 0:
                    value = [
                        UUID(s)
                        for s in list(
                            filter(
                                lambda s: len(s.strip()) > 0,
                                [item.strip() for item in value.split(",")],
                            )
                        )
                    ]
                else:
                    value = None

            # FROM MAPPING
            elif isinstance(value, Mapping):
                if "id" in value:
                    value = cls.uuid_list(value["id"])

                raise ValueError(f"Error validate, object not constains key id", value)

            # FROM SEQUENCE
            elif isinstance(value, Sequence):
                validated = None
                for item in value:
                    item = cls.uuid_list(item)
                    if item is not None:
                        if validated is not None:
                            validated += item
                        else:
                            validated = item

                value = validated

            # FROM OBJECT
            elif isinstance(value, object):
                if hasattr(value, "id"):
                    value = cls.uuid_list(getattr(value, "id"))

                raise ValueError(
                    f"Error validate, object not constains attribute id", value
                )

            return value

        @classmethod
        def str_list(
            cls,
            value: Union[str, list[str], None],
            split_str: Optional[str] = ",",
        ) -> Union[list[str], None]:
            if value is not None:
                if isinstance(value, str):
                    value = value.strip()
                    if len(value) == 0:
                        value = None

                    else:
                        if split_str is not None:
                            value = [
                                item.strip()
                                for item in list(
                                    filter(lambda s: len(s) > 0, value.split(split_str))
                                )
                            ]
                        else:
                            value = [value]

            return value

        @classmethod
        def time(
            cls,
            value: Union[pydatetime.datetime, pydatetime.time, str, None],
            format: str = DEFAULT_TIME_FORMAT,
        ) -> Union[pydatetime.time, None]:
            if value is not None:
                if isinstance(value, pydatetime.datetime):
                    value = value.time()
                elif isinstance(value, str):
                    value = pydatetime.datetime.strptime(value, format).time()

            return value

        @classmethod
        def date(
            cls,
            value: Union[pydatetime.datetime, pydatetime.date, str, None],
            format: str = DEFAULT_DATE_FORMAT,
        ) -> Union[pydatetime.date, None]:
            if value is not None:
                if isinstance(value, pydatetime.datetime):
                    value = value.date()
                elif isinstance(value, str):
                    value = pydatetime.datetime.strptime(value, format).date()

            return value

        @classmethod
        def datetime(
            cls,
            value: Union[pydatetime.datetime, str, None],
            format: str = DEFAULT_DATETIME_FORMAT,
        ) -> Union[pydatetime.datetime, None]:
            if value is not None and isinstance(value, str):
                value = pydatetime.datetime.strptime(value, format)

            return value

        @classmethod
        def timedelta(
            cls, value: Union[pydatetime.timedelta, str, int, float, None]
        ) -> Union[pydatetime.timedelta, None]:
            if value is not None:
                if isinstance(value, str):
                    return pydatetime.timedelta(seconds=int(value))
                elif isinstance(value, int) or isinstance(value, float):
                    return pydatetime.timedelta(seconds=value)

            return value

        @classmethod
        def model(
            cls,
            value: Union[any, None],
            model_cls: type[BaseModel],
            base_field: str,
        ) -> Union[type[BaseModel], None]:
            if value is not None:
                if isinstance(value, model_cls):
                    return value

                elif isinstance(value, dict):
                    return model_cls.model_validate(value)

                else:
                    return model_cls.model_validate({base_field: value})

            return None

        @classmethod
        def model_list(
            cls,
            values: Union[Sequence[any], None],
            model_cls: type[BaseModel],
            base_field: str,
        ) -> Union[list[type[BaseModel]], None]:
            if values is not None:
                return [
                    PydanticHelper.validators.model(
                        value=v, model_cls=model_cls, base_field=base_field
                    )
                    for v in values
                ]

            return None

        @classmethod
        def enum(
            cls,
            value: Union[any, None],
            enum_cls: type[Enum],
        ) -> Union[type[Enum], None]:
            if value is not None:
                if isinstance(value, enum_cls):
                    return value
                else:
                    return enum_cls(value)

            return None

        @classmethod
        def enum_list(
            cls,
            values: Union[Sequence[any], None],
            model_cls: type[Enum],
        ) -> Union[list[type[Enum]], None]:
            if values is not None:
                return [
                    PydanticHelper.validators.enum(value=v, model_cls=model_cls)
                    for v in values
                ]

            return None

    class serializers:
        """Сериализаторы"""

        @classmethod
        def uuid(
            cls,
            value: Union[UUID, None],
        ) -> str:
            return str(value) if value is not None else None

        @classmethod
        def uuid_list(
            cls,
            value: Union[list[UUID], None],
        ) -> Union[list[str], None]:
            return [str(v) for v in value] if value is not None else None

        @classmethod
        def str_list(
            cls,
            value: Union[list[str], None],
            join_str: str = ",",
        ) -> Union[str, None]:
            return join_str.join(value) if value is not None else None

        @classmethod
        def time(
            cls,
            value: Union[pydatetime.time, None],
            format: str = DEFAULT_TIME_FORMAT,
        ) -> Union[str, None]:
            return value.strftime(format) if value is not None else None

        @classmethod
        def date(
            cls,
            value: Union[pydatetime.date, None],
            format: str = DEFAULT_DATE_FORMAT,
        ) -> Union[str, None]:
            return value.strftime(format) if value is not None else None

        @classmethod
        def datetime(
            cls,
            value: Union[pydatetime.datetime, None],
            format: str = DEFAULT_DATETIME_FORMAT,
        ) -> Union[str, None]:
            return value.strftime(format) if value is not None else None

        @classmethod
        def timedelta(
            cls, value: Union[pydatetime.timedelta, None]
        ) -> Union[float, None]:
            if value is not None:
                return value.total_seconds()
            return None

        @classmethod
        def enum(
            cls,
            value: Union[type[Enum], None],
        ) -> Union[any, None]:
            if value is not None:
                return value.value
            return None

        @classmethod
        def enum_list(
            cls,
            value: Union[list[type[Enum]], None],
            join_str: str = ",",
        ) -> Union[str, None]:
            return (
                join_str.join([i.value for i in value]) if value is not None else None
            )

    class mixins:
        """Миксины"""
        
        def bool(*field_names, true_list: list[str] = DEFAULT_TRUE_LIST):
            class Mixin:
                # Валидатор
                @field_validator(*field_names, mode="before")
                def uuid_validator(cls, v):
                    return PydanticHelper.validators.bool(v, true_list=true_list)

            return Mixin

        def uuid(*field_names):
            class Mixin:
                # Валидатор
                @field_validator(*field_names, mode="before")
                def uuid_validator(cls, v):
                    return PydanticHelper.validators.uuid(v)

                # Сериализатор
                @field_serializer(*field_names)
                def uuid_serializer(self, v, _):
                    return PydanticHelper.serializers.uuid(v)

            return Mixin

        def uuid_list(*field_names):
            class Mixin:
                # Валидатор
                @field_validator(*field_names, mode="before")
                def uuid_validator(cls, v):
                    return PydanticHelper.validators.uuid_list(v)

                # Сериализатор
                @field_serializer(*field_names)
                def uuid_serializer(self, v, _):
                    return PydanticHelper.serializers.uuid_list(v)

            return Mixin

        def str_list(*field_names):
            class Mixin:
                # Валидатор
                @field_validator(*field_names, mode="before")
                def str_list_validator(cls, v):
                    return PydanticHelper.validators.str_list(v)

                # Сериализатор
                @field_serializer(*field_names)
                def str_list_serializer(self, v, _):
                    return PydanticHelper.serializers.str_list(v)

            return Mixin

        def time(*field_names, format: str = DEFAULT_TIME_FORMAT):
            class Mixin:
                # Валидатор
                @field_validator(*field_names, mode="before")
                def time_validator(cls, v):
                    return PydanticHelper.validators.time(v, format=format)

                # Сериализатор
                @field_serializer(*field_names)
                def time_serializer(self, v, _):
                    return PydanticHelper.serializers.time(v, format=format)

            return Mixin

        def date(*field_names, format: str = DEFAULT_DATE_FORMAT):
            class Mixin:
                # Валидатор
                @field_validator(*field_names, mode="before")
                def date_validator(cls, v):
                    return PydanticHelper.validators.date(v, format=format)

                # Сериализатор
                @field_serializer(*field_names)
                def date_serializer(self, v, _):
                    return PydanticHelper.serializers.date(v, format=format)

            return Mixin

        def datetime(*field_names, format: str = DEFAULT_DATETIME_FORMAT):
            class Mixin:
                # Валидатор
                @field_validator(*field_names, mode="before")
                def datetime_validator(cls, v):
                    return PydanticHelper.validators.datetime(v, format=format)

                # Сериализатор
                @field_serializer(*field_names)
                def datetime_serializer(self, v, _):
                    return PydanticHelper.serializers.datetime(v, format=format)

            return Mixin

        def timedelta(*field_names):
            class Mixin:
                # Валидатор
                @field_validator(*field_names, mode="before")
                def timedelta_validator(cls, v):
                    return PydanticHelper.validators.timedelta(v)

                # Сериализатор
                @field_serializer(*field_names)
                def timedelta_serializer(self, v, _):
                    return PydanticHelper.serializers.timedelta(v)

            return Mixin

        def model(*field_names, model_cls: type[BaseModel], base_field: str = "id"):
            class Mixin:
                # Валидатор
                @field_validator(*field_names, mode="before")
                def model_validator(cls, v):
                    return PydanticHelper.validators.model(
                        v, model_cls=model_cls, base_field=base_field
                    )

            return Mixin

        def model_list(
            *field_names, model_cls: type[BaseModel], base_field: str = "id"
        ):
            class Mixin:
                # Валидатор
                @field_validator(*field_names, mode="before")
                def model_validator(cls, v):
                    return PydanticHelper.validators.model_list(
                        v, model_cls=model_cls, base_field=base_field
                    )

            return Mixin

        # def enum(*field_names, enum_cls: type[Enum]):
        #     class Mixin:
        #         # Валидатор
        #         @field_validator(*field_names, mode="before")
        #         def enum_validator(cls, v):
        #             return PydanticHelper.validators.enum(v, enum_cls=enum_cls)

        #         # Сериализатор
        #         @field_serializer(*field_names)
        #         def enum_serializer(self, v, _):
        #             return PydanticHelper.serializers.enum(v)

        #     return Mixin

        def enum(*field_names, enum_cls: type[Enum]) -> type:
            prefix = f"{enum_cls.__name__}"

            validator_name = f"{prefix}_validator"
            serializer_name = f"{prefix}_serializer"

            def make_validator() -> Callable:
                @field_validator(*field_names, mode="before")
                def _validator(cls, v):
                    return PydanticHelper.validators.enum(v, enum_cls=enum_cls)

                return _validator

            def make_serializer() -> Callable:
                @field_serializer(*field_names)
                def _serializer(self, v, _info):
                    return PydanticHelper.serializers.enum(v)

                return _serializer

            attrs = {
                validator_name: make_validator(),
                serializer_name: make_serializer(),
            }

            # Создаём миксин динамически, чтобы имена были уникальными
            return type(f"{prefix}Mixin", (object,), attrs)

        def enum_list(*field_names, enum_cls: type[Enum]):
            class Mixin:
                # Валидатор
                @field_validator(*field_names, mode="before")
                def enum_validator(cls, v):
                    return PydanticHelper.validators.enum_list(v, enum_cls=enum_cls)

                # Сериализатор
                @field_serializer(*field_names)
                def enum_serializer(self, v, _):
                    return PydanticHelper.serializers.enum_list(v)

            return Mixin


__all__ = ["PydanticHelper"]
