from abc import ABC, abstractmethod
from pydantic import TypeAdapter
from ..setting import EventSetting
from ..authentication import AuthRequests
from ..datastructures import EventRequestSchema


class EventRequestService(ABC):

    @abstractmethod
    def send(
        self,
        events: list[EventRequestSchema],
    ):
        """Отправить событие"""


class BaseEventRequestService(EventRequestService):

    def __init__(
        self,
        trusted: AuthRequests,
        setting: EventSetting,
    ):
        super().__init__()
        self.t = trusted
        self.s = setting

    def send(
        self,
        events: list[EventRequestSchema],
    ):
        self.t.post(
            f"{self.s.url}/push",
            json=TypeAdapter(list[EventRequestSchema]).dump_python(events),
            headers={ 'Content-Type': 'application/json;charset=UTF-8' },
            retries=self.s.retries,
            error_delay=self.s.error_delay_sec,
            check_responce=lambda x: x.status_code == 200,
            wait_result=False,
        )


def create_event_request_service(
    trusted,
    setting: EventSetting,
) -> EventRequestService:
    return BaseEventRequestService(
        trusted=trusted,
        setting=setting,
    )


def send_event_request(
    trusted,
    setting: EventSetting,
    events: list[EventRequestSchema],
):
    return create_event_request_service(
        trusted=trusted,
        setting=setting,
    ).send(events=events)


__all__ = [
    "EventRequestService",
    "send_event_request",
    "create_event_request_service",
]
