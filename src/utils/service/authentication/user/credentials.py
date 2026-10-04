from ..service import AuthCredentialsMixin, AuthBackendMixin
from ..backend import inject_credentials
from ...datastructures.auth import AuthData


class UserCredentials(AuthCredentialsMixin):
    def __init__(
        self,
        data: AuthData,
        backend: AuthBackendMixin,
    ):
        super().__init__()
        self._d = data
        self._b = backend

    @property
    def credentials(self) -> dict:
        return self._b.credentias(self._d.jwt)

    def inject_credentials(self, **kwarks) -> dict[str, any]:
        return inject_credentials(self.credentials, **kwarks)

    def reset_credentials(self):
        return self._b.logout(self._d.jwt)

    def url_credentials(self) -> dict[str, str]:
        return self._b.url_credentials(self._d.jwt)