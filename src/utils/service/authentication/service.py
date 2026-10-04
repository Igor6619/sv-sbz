import abc
from requests import Response
from typing import Callable, Optional
from ..datastructures import User, Token, AuthData
from ..setting import AuthClientSetting


class AuthUserMixin(abc.ABC):
    """Содержит информацию о пользователе"""

    @property
    @abc.abstractmethod
    def user(self) -> User:
        """Пользователь"""


class AuthCredentialsMixin(abc.ABC):
    """Содержит учетные данные"""

    @property
    @abc.abstractmethod
    def credentials(self) -> dict:
        """Учетные данные для выполнения запросов"""

    @abc.abstractmethod
    def inject_credentials(self, **kwarks) -> dict[str, any]:
        """Инъекция учетных данных"""

    @abc.abstractmethod
    def reset_credentials(self):
        """Сбросить текущие учетные данные, в дальнейшем потребуется их обновление"""

    @abc.abstractmethod
    def url_credentials(self) -> dict[str, str]:
        """Учетные данные для вставки в query URL"""


class AuthRequestsMixin(abc.ABC):
    @abc.abstractmethod
    def get(
        self,
        url,
        params=None,
        retries=1,
        error_delay=3,
        wait_result: bool = True,
        check_responce: Optional[Callable[[Response], bool]] = None,
        **kwargs,
    ) -> Response: ...

    @abc.abstractmethod
    def post(
        self,
        url,
        data=None,
        json=None,
        retries=1,
        error_delay=3,
        wait_result: bool = True,
        check_responce: Optional[Callable[[Response], bool]] = None,
        **kwargs,
    ) -> Response: ...

    @abc.abstractmethod
    def put(
        self,
        url,
        data=None,
        retries=1,
        error_delay=3,
        wait_result: bool = True,
        check_responce: Optional[Callable[[Response], bool]] = None,
        **kwargs,
    ) -> Response: ...

    @abc.abstractmethod
    def patch(
        self,
        url,
        data=None,
        retries=1,
        error_delay=3,
        wait_result: bool = True,
        check_responce: Optional[Callable[[Response], bool]] = None,
        **kwargs,
    ) -> Response: ...

    @abc.abstractmethod
    def delete(
        self,
        url,
        retries=1,
        error_delay=3,
        wait_result: bool = True,
        check_responce: Optional[Callable[[Response], bool]] = None,
        **kwargs,
    ) -> Response: ...


class AuthRequests(AuthRequestsMixin, AuthCredentialsMixin):
    """Модуль выполнения запросов"""


class AuthUserEnvrimoment(AuthUserMixin):
    """Представление окружение функций пользователя"""

    @property
    @abc.abstractmethod
    def requests(self) -> AuthRequests:
        """Модуль обмена от имени пользователя"""

    @property
    @abc.abstractmethod
    def remote_requests(self) -> AuthRequests:
        """Модуль обмена от имени пользователя с внешними системами"""


class AuthTrustedClient(AuthUserMixin, AuthCredentialsMixin, AuthRequestsMixin):
    """Клиент защищеного обмена данными"""


class AuthBackendMixin(abc.ABC):
    """Утилиты для отработки данных клиента"""

    @property
    @abc.abstractmethod
    def setting(self) -> AuthClientSetting:
        """"""

    @abc.abstractmethod
    def validate(self, jwt: str) -> tuple[User, Token]:
        """"""

    @abc.abstractmethod
    def logout(self, jwt: str):
        """"""

    @abc.abstractmethod
    def update(self, jwt: str) -> str:
        """"""

    @abc.abstractmethod
    def credentias(self, jwt: str) -> dict:
        """"""

    @abc.abstractmethod
    def remote_credentials(self, jwt: str) -> dict:
        """"""

    @abc.abstractmethod
    def url_credentials(self, jwt: str) -> dict[str, str]:
        """Учетные данные для вставки в query URL"""

class AuthClient(abc.ABC):
    @property
    @abc.abstractmethod
    def version(self) -> str: ...

    @property
    @abc.abstractmethod
    def setting(self) -> AuthClientSetting:
        """"""

    @property
    @abc.abstractmethod
    def trusted(self) -> AuthTrustedClient: ...

    @abc.abstractmethod
    def user_env(self, auth: AuthData) -> AuthUserEnvrimoment:
        """Получить окружение пользователя"""
