from requests import Response
from .credentials import TrustedCredentials
from ..service import AuthBackendMixin, AuthTrustedClient
from ..backend import ThreadRequests
from ...datastructures.auth import User, UserBaseProviders


class TrustedClient(AuthTrustedClient):
    def __init__(
        self,
        backend: AuthBackendMixin,
    ):
        super().__init__()
        self._b = backend
        self._c = TrustedCredentials(backend)

    @property
    def user(self) -> User:
        return (
            User(
                id=self._b.setting.trusted.auth.username,
                provider=UserBaseProviders.Trusted,
            )
            if self._b.setting.trusted.auth is not None
            else None
        )
    
    @property
    def credentials(self) -> dict: return self._c.credentials

    def inject_credentials(self, **kwarks) -> dict[str, any]:
        return self._c.inject_credentials(**kwarks)

    def reset_credentials(self):
        return self._c.reset_credentials()
    
    def url_credentials(self):
        return self._c.url_credentials()

    def get(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return ThreadRequests(credentials=self._c).get(*args, **kwargs)

    def post(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return ThreadRequests(credentials=self._c).post(*args, **kwargs)

    def put(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return ThreadRequests(credentials=self._c).put(*args, **kwargs)

    def patch(
        self,
        *args,
        **kwargs,
    ):
        return ThreadRequests(credentials=self._c).patch(*args, **kwargs)

    def delete(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return ThreadRequests(credentials=self._c).delete(*args, **kwargs)
