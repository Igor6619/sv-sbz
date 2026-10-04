from ...setting.auth import AuthClientSetting
from ...datastructures.auth import TrustedNodeJwt

from ..service import AuthCredentialsMixin, AuthBackendMixin
from ..backend import inject_credentials
import jwt as jwt_lib
from uuid import uuid4

from datetime import datetime, timezone
from threading import Lock
from requests import post
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes

ALGORITM = "RS256"


class TrustedCredentials(AuthCredentialsMixin):
    def __init__(
        self,
        backend: AuthBackendMixin,
    ):
        super().__init__()
        self._k = None
        self._b = backend
        self._l = Lock()
        self._cred: dict[str, any] | None = None

    @property
    def credentials(self) -> dict:
        with self._l:
            if self._cred is not None:
                return self._cred

        r = post(
            f"{self._b.setting.url}/v{self._b.setting.version}/login?provider=trusted",
            json={
                "username": (
                    self._b.setting.trusted.auth.username
                    if self._b.setting.trusted.auth is not None
                    else None
                ),
                "jwt": self.gen_jwt,
            },
        )
        if r.status_code == 200:
            with self._l:
                self._cred = {"headers": {"Token": r.json()["token"]}}

                return self._cred
        else:
            raise Exception(f"Ошибка доверенного входа: {r.status_code}")

        return self._cred

    def inject_credentials(self, **kwarks) -> dict[str, any]:
        return inject_credentials(self.credentials, **kwarks)

    def reset_credentials(self):
        with self._l:
            self._cred = None

    def url_credentials(self) -> dict[str, str]:
        return {"token": self.credentials["headers"]["Token"]}

    @property
    def gen_jwt(self) -> str:
        payload = TrustedNodeJwt(
            id=str(uuid4()),
            created=datetime.now(timezone.utc).replace(tzinfo=None),
        ).model_dump()
        return jwt_lib.encode(
            payload,
            key=self.private_key,
            algorithm=ALGORITM,
        )

    @property
    def private_key(self) -> PrivateKeyTypes:
        if self._k is None:
            if self._b.setting.trusted.auth is None:
                raise Exception("Trusted client setting not found")

            with open(self._b.setting.trusted.auth.private_key, "rb") as f:
                self._k = serialization.load_pem_private_key(
                    f.read(),
                    password=self._b.setting.trusted.auth.private_key_password,
                    backend=default_backend(),
                )

        return self._k
