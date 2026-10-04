from .service import *
from .client import *

__all__ = [
    "AuthClient",
    "AuthRequests",
    "AuthUserEnvrimoment",
    "AuthTrustedClient",
    "auth_client",
    "auth_trusted_client",
]

import importlib.util

if importlib.util.find_spec("fastapi"):
    from .middleware import *

    __all__.append("init_auth_fastapi_backend")
