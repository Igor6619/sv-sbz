from .service import AuthClient, AuthTrustedClient, AuthUserEnvrimoment
from ..setting import AuthClientSetting

from .user import UserEnvrimomemnt
from .backend import AuthBackend
from .trusted import TrustedClient


class Client(AuthClient):

    def __init__(
        self,
        setting: AuthClientSetting,
    ):
        super().__init__()
        self._b = AuthBackend(setting)
        self._t = None

    @property
    def backend(self):
        return self._b
    
    @property
    def version(self) -> str:
        return self._b.setting.version
    
    @property
    def setting(self) -> AuthClientSetting:
        return self._b.setting

    @property
    def trusted(self) -> AuthTrustedClient:
        if self._t is None:
            self._t = TrustedClient(self._b)

        return self._t

    def user_env(self, auth) -> AuthUserEnvrimoment:
        return UserEnvrimomemnt(data=auth, backend=self._b)


GLOBAL_AUTH_CLIENT = None


def auth_client(
    setting: AuthClientSetting = None,
) -> AuthClient:
    """Метод получение клиента аутентификации, автоматически создает при отсутсвии"""

    global GLOBAL_AUTH_CLIENT
    if GLOBAL_AUTH_CLIENT is not None:
        return GLOBAL_AUTH_CLIENT

    if setting is None:
        from ..setting import get_sub_setting

        setting = get_sub_setting(id="auth.client", model=AuthClientSetting)

    from .client import Client

    GLOBAL_AUTH_CLIENT = Client(setting=setting)
    return GLOBAL_AUTH_CLIENT


def auth_trusted_client(
    setting: AuthClientSetting = None,
) -> AuthTrustedClient:
    return auth_client(setting=setting).trusted
