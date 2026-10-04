__all__ = []

import importlib.util

if importlib.util.find_spec("fastapi"):
    from .auth import *
    from .events import *
    from .workplaces import *

    modules = {
        # AUTH
        "AuthRequired": AuthRequired,
        "AuthPermissionRequired": AuthPermissionRequired,
        "TrustedRequired": TrustedRequired,
        "AuthEnvrimomentOrNone": AuthEnvrimomentOrNone,
        "AuthPermissionsOrNone": AuthPermissionsOrNone,
        # EVENTS
        "EventsRequired": EventsRequired,
        "TrustedEventsRequired": TrustedEventsRequired,
        # WORKPLACES
        "WorkplaceServiceRequired": WorkplaceServiceRequired,
    }
    __all__.extend(modules.keys())
    globals().update(modules)
