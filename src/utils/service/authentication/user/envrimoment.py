from ...datastructures.auth import User, AuthData
from ..service import AuthBackendMixin, AuthUserEnvrimoment, AuthRequests


class UserEnvrimomemnt(AuthUserEnvrimoment):
    def __init__(
        self,
        data: AuthData,
        backend: AuthBackendMixin,
    ):
        super().__init__()
        self._d = data
        self._b = backend
        self._r = None
        self._rr = None

    @property
    def user(self) -> User:
        return self._d.user

    @property
    def requests(self) -> AuthRequests:
        if self._r is None:
            from .credentials import UserCredentials
            from ..backend import ThreadRequests

            self._r = ThreadRequests(
                UserCredentials(
                    data=self._d,
                    backend=self._b,
                )
            )
        return self._r

    @property
    def remote_requests(self) -> AuthRequests:
        if self._rr is None:
            from .remote_credentials import UserRemoteCredentials
            from ..backend import ThreadRequests

            self._rr = ThreadRequests(
                UserRemoteCredentials(
                    data=self._d,
                    backend=self._b,
                )
            )
        return self._rr
