import fastapi
from .auth import AuthRequired
from ..authentication import AuthUserEnvrimoment
from ..applications import WorkplaceService, create_workplaces_service


async def WorkplaceServiceRequired(
    env: AuthUserEnvrimoment = fastapi.Depends(AuthRequired),
) -> WorkplaceService:
    return create_workplaces_service(env.requests)


__all__ = ["WorkplaceServiceRequired"]
