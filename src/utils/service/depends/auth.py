import fastapi
from ..datastructures import AuthData, JwtTokenCredentials, UserBaseProviders
from ..authentication import auth_client, AuthUserEnvrimoment


async def AuthEnvrimomentOrNone(
    request: fastapi.Request,
    jwt_token: JwtTokenCredentials = fastapi.Header(),  # Инъекция для генерации корректной документации
) -> AuthUserEnvrimoment | None:
    if request.state.user is not None and request.state.token is not None:
        return auth_client().user_env(
            auth=AuthData(
                jwt=request.state.jwt,
                user=request.state.user,
                token=request.state.token,
            )
        )

    return None


def AuthPermissionsOrNone(
    permissions: list[any],
):
    async def func(
        env: AuthUserEnvrimoment = fastapi.Depends(AuthEnvrimomentOrNone),
    ):
        if env is not None: 
            for p in env.user.permissions:
                if str(p) in permissions:
                    return env

        return None

    return func


async def AuthRequired(
    env: AuthUserEnvrimoment | None = fastapi.Depends(AuthEnvrimomentOrNone),
) -> AuthUserEnvrimoment:
    if env is not None:
        return env
    raise fastapi.HTTPException(401)


def AuthPermissionRequired(
    permissions: list[any],
):
    async def func(
        env: AuthUserEnvrimoment = fastapi.Depends(AuthPermissionsOrNone(permissions)),
    ):
        if env is None:
            return fastapi.HTTPException(status_code=403)

        return env

    return func


async def TrustedRequired(
    env: AuthUserEnvrimoment = fastapi.Depends(AuthRequired),
) -> AuthUserEnvrimoment:
    if env.user.provider == UserBaseProviders.Trusted:
        return env
    raise fastapi.HTTPException(403)


__all__ = [
    "AuthRequired",
    "AuthPermissionRequired",
    "TrustedRequired",
    "AuthEnvrimomentOrNone",
    "AuthPermissionsOrNone",
]
