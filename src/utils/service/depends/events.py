from typing import Callable
from fastapi import Depends, Body
from ..setting import EventSetting
from ..datastructures import EventSchema
from .auth import TrustedRequired


def EventsRequired(
    events: EventSchema | list[EventSchema] = Body(),
) -> list[EventSchema]:
    if isinstance(events, EventSchema):
        events = [events]
    return events


def TrustedEventsRequired(setting: EventSetting) -> Callable:
    from .events import EventsRequired

    def events_required(
        env=Depends(TrustedRequired),
        events=Depends(EventsRequired),
    ) -> list[EventSchema]:
        return events

    return events_required


__all__ = [
    "EventsRequired",
    "TrustedEventsRequired",
]
