import os
import uuid
import requests
import fastapi
from depends import *
from fastapi.templating import Jinja2Templates
from utils.service.depends import AuthEnvrimomentOrNone
from utils.service.authentication import auth_client, AuthUserEnvrimoment
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

base_router = fastapi.routing.APIRouter()
templates = Jinja2Templates(
    directory=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    )
)


@base_router.get("/")
async def main_page():
    return fastapi.responses.RedirectResponse("/files")


@base_router.get("/login")
async def login(
    request: fastapi.Request,
    id: str = fastapi.Query(None),
    back: str = fastapi.Query(None),
    env: AuthUserEnvrimoment = fastapi.Depends(AuthEnvrimomentOrNone),
):
    if back is None:
        back = "/"

    if env is not None:
        return fastapi.responses.RedirectResponse("/")

    if id is not None:
        try:
            r = requests.get(f"{auth_client().setting.url}/v1/sso/get?id={id}").json()
            token = r["token"]

            responce = fastapi.responses.RedirectResponse(back)
            responce.set_cookie(
                "Token", token, domain=request.base_url.hostname
            )

            return responce
        except Exception as ex:
            print(f'Ошибка получения учетных данных', ex)

    else:
        id = uuid.uuid4()
        back_url = request.url
        back_url.include_query_params(
            id=str(id),
            back=back,
        )

        url = urlparse(f"{auth_client().setting.url}/v1/sso")
        url = url._replace(
            query=urlencode(
                parse_qsl(url.query) + [("id", id), ("back", str(back_url))]
            )
        )
        print(id, url, back_url)
        return fastapi.responses.RedirectResponse(urlunparse(url))

    return fastapi.responses.RedirectResponse("/")


@base_router.get("/logout")
async def logout(
    request: fastapi.Request,
    back: str = fastapi.Query(None),
    env: AuthUserEnvrimoment = fastapi.Depends(AuthEnvrimomentOrNone),
):
    if env is not None:
        auth = auth_client()
        env.requests.post(f"{auth.setting.url}/v{auth.setting.version}/logout")
        request.state.user = None
        request.state.jwt = None
        request.state.token = None

    responce = fastapi.responses.RedirectResponse(back if back is not None else "/")
    responce.set_cookie(
        "Token", "", domain=request.base_url.hostname
    )

    return responce


__all__ = ["base_router"]
