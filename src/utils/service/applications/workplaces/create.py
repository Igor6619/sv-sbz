from .base import BaseWorkplaceService
from .service import WorkplaceService
from ...authentication import AuthRequests, auth_client

def create_workplaces_service(auth: AuthRequests) -> WorkplaceService: 
    return BaseWorkplaceService(
        requests=auth,
        setting=auth_client().setting,
    )