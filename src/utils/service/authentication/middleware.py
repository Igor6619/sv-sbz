import asyncio
import requests
import importlib.util

if importlib.util.find_spec("fastapi"):
    import fastapi
    import datetime
    import starlette.middleware.base
    from .service import AuthBackendMixin
    from ..setting import AuthClientSetting
    from ..datastructures import (
        JwtTokenCredentials,
        JwtTokenQueryCredentials,
        UserBaseProviders,
    )
    from .client import auth_client

    class AuthMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
        def __init__(self, app, dispatch=None):
            super().__init__(app, dispatch)
            self.backend: AuthBackendMixin = auth_client().backend

        async def dispatch(self, request, call_next):
            request.state.user = None
            request.state.token = None
            request.state.jwt = None

            api_key = None
            jwt_data = None
            query = JwtTokenQueryCredentials.model_validate(request.query_params)
            cokies = JwtTokenCredentials.model_validate(request.cookies)
            headers = JwtTokenCredentials.model_validate(request.headers)

            if query.token is not None:
                jwt_data = query.token
            elif headers.Token is not None:
                jwt_data = headers.Token
            elif cokies.Token is not None:
                jwt_data = cokies.Token

            if query.apikey is not None:
                api_key = query.apikey
            elif headers.ApiKey is not None:
                api_key = headers.ApiKey
            elif cokies.ApiKey is not None:
                api_key = cokies.ApiKey

            if jwt_data is not None:
                await self._handle_token(jwt_data=jwt_data, request=request)

            if api_key is not None and request.state.user is None:
                login_request = await asyncio.to_thread(
                    requests.post,
                    f"{self.backend.setting.url}/v{self.backend.setting.version}/login",
                    json={"apikey": api_key},
                    headers={"Content-Type": "application/json"},
                )
                if login_request.status_code == 200:
                    jwt_data = login_request.json().get("token", None)
                    if jwt_data is not None:
                        await self._handle_token(jwt_data=jwt_data, request=request)

            responce: fastapi.Response = await call_next(request)
            if request.state.user is not None: 
                cred = JwtTokenCredentials(Token=jwt_data)
                for k, v in cred.model_dump(exclude_none=True).items():
                    responce.headers[k] = v
                    responce.set_cookie(k, v)
            return responce

        async def _handle_token(self, jwt_data: str, request):
            try:
                user, token = self.backend.validate(jwt=jwt_data)
                life_balance: int = (
                    token.access_expires
                    - datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                ).total_seconds()
                if life_balance < self.backend.setting.min_jwt_balance_sec:
                    try:
                        jwt_data = await asyncio.to_thread(
                            self.backend.update, jwt=jwt_data
                        )
                        user, token = await asyncio.to_thread(
                            self.backend.validate, jwt=jwt_data
                        )
                    except Exception as ex:
                        print(f"Error update jwt token: {str(ex)}")

                if user is not None and user.provider == UserBaseProviders.Trusted:
                    if not self.backend.setting.trusted.enable:
                        user = None
                        token = None
                        jwt_data = None
                    elif (
                        self.backend.setting.trusted.white_list is not None
                        and request.client.host
                        not in self.backend.setting.trusted.white_list
                    ):
                        user = None
                        token = None
                        jwt_data = None

                request.state.user = user
                request.state.token = token
                request.state.jwt = jwt_data
            except Exception as ex:
                print(f"Error handle jwt: {str(ex)}")

    def init_auth_fastapi_backend(
        app: fastapi.FastAPI,
        setting: AuthClientSetting,
    ):
        from .middleware import AuthMiddleware

        if setting.version == str(1):
            if app is not None:
                app.add_middleware(AuthMiddleware)
