import os
import requests as requests
from datetime import datetime, timezone
from pydantic import BaseModel
from ..service import AuthBackendMixin
from ...datastructures.auth import *
from ...setting.auth import AuthClientSetting


class UserData(BaseModel):
    user: User
    valid: bool
    updated: datetime
    last_used: datetime


class RemoteCredentialsData(BaseModel):
    data: dict
    valid: bool
    updated: datetime
    last_used: datetime


class AuthBackend(AuthBackendMixin):

    def __init__(
        self,
        setting: AuthClientSetting,
    ):
        super().__init__()
        self.retries = 3
        self._s = setting
        self._users = dict[str, UserData]()
        self._rcred = dict[str, RemoteCredentialsData]()
        self._public_key = None

    @property
    def setting(self) -> AuthClientSetting:
        return self._s

    def validate(self, jwt: str) -> tuple[User, Token]:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        import jwt as jwt_lib

        jwt_data = jwt_lib.decode(jwt=jwt, key=self.public_key(), algorithms=["RS256"])
        token = Token.model_validate(jwt_data)

        if token.access_expires < now:
            raise Exception(f"Token expired")

        if token.user in self._users:
            return self._users[token.user].user, token

        r = requests.get(
            url=self.make_route("user"),
            **self.credentias(jwt=jwt),
        )

        if r.status_code == 200:
            user = User.model_validate(r.json())
            self._users[user.uuid] = UserData(
                user=user,
                valid=True,
                updated=now,
                last_used=now,
            )
            return user, token
        else:
            raise Exception(f"Error responce: {r.status_code}: {r.text}")

    def logout(self, jwt: str):
        return (
            requests.post(
                url=self.make_route("logout"),
                **self.credentias(jwt),
            ).status_code
            == 200
        )

    def update(self, jwt: str) -> str:
        responce = requests.post(url=self.make_route("update"), **self.credentias(jwt))
        if responce.status_code == 200:
            return responce.json().get("token", "")

        raise Exception(f"{responce.status_code}")

    def credentias(self, jwt: str) -> dict:
        return {"headers": JwtTokenCredentials(Token=jwt).model_dump(exclude_none=True)}

    def remote_credentials(self, jwt: str) -> dict:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        r = requests.get(
            url=self.make_route("credentials"),
            **self.credentias(jwt),
        )

        if r.status_code == 200:
            data: dict = r.json()
            data = {k: v for k, v in data.items() if k is not None and v is not None}
            self._rcred[jwt] = RemoteCredentialsData(
                data=data, valid=True, updated=now, last_used=now
            )
            return data

        return {}

    def url_credentials(self, jwt: str) -> dict[str, str]:
        return {"token": jwt}

    def public_key(self) -> any:
        if self._public_key is not None:
            return self._public_key
        elif self._s.public_key is not None and os.path.exists(self._s.public_key):
            try:
                from cryptography.hazmat.backends import default_backend
                from cryptography.hazmat.primitives import serialization

                with open(self._s.public_key, "rb") as f:
                    self._public_key = serialization.load_pem_public_key(
                        f.read(), backend=default_backend()
                    )
                return self._public_key
            except Exception as ex:
                import traceback

                raise Exception(
                    f"Error load public {str(ex)}\n{traceback.format_exc()}"
                )

        for i in range(self.retries):
            try:
                responce = requests.get(url=self.make_route("public_key"))
                if responce.status_code == 200:
                    from cryptography.hazmat.backends import default_backend
                    from cryptography.hazmat.primitives import serialization

                    key_data: bytes = responce.content
                    self._public_key = serialization.load_pem_public_key(
                        key_data, backend=default_backend()
                    )
                    return self._public_key

            except Exception as ex:
                import traceback

                print(f"Error get public key: {str(ex)}\n{traceback.format_exc()}")

        raise Exception(f"Public key not found")

    def make_route(self, route: str) -> str:
        return f"{self._s.url}/v{self._s.version}/{route}"
