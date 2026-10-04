from threading import Thread
from requests import Response
from requests.exceptions import RequestException
from typing import Callable, Optional
from requests import get, post, put, patch, delete, Response
from ..service import AuthCredentialsMixin, AuthRequestsMixin


class ThreadRequestTask:
    """Модуль отправки запросов в потоке"""

    def __init__(
        self,
        backend: AuthCredentialsMixin,
    ):
        self._b = backend
        self._result = None
        self._thread = Thread(target=self.__call__, daemon=True)

    def start(
        self,
        request_method,
        retries: int = 1,
        error_delay: float = 3,
        wait_result: bool = True,
        check_responce: Optional[Callable[[Response], bool]] = None,
        **kwarks,
    ):
        self._req = request_method
        self._retries = retries
        self._delay = error_delay
        self._check = check_responce

        self._kwarks = kwarks

        self._thread.start()
        if wait_result:

            self._thread.join()
            if isinstance(self._result, Exception):
                raise self._result

            return self._result

        return None

    def __call__(self, *args, **kwds):
        last_ex: Exception | None = None
        index = 0
        while index < self._retries:
            index += 1
            try:
                print("query", self._kwarks.get("url", None))
                self._result: Response = self._req(
                    **self._b.inject_credentials(**self._kwarks)
                )
                if self._result.status_code == 401:
                    self._b.reset_credentials()
                    if index == 1:
                        self._retries += 1
                    raise RequestException(f"Error code: {self._result.status_code}")

                if self._check is None:
                    self._b = None
                    return
                elif self._check(self._result):
                    self._b = None
                    return
                else:
                    raise RequestException(f"Error code: {self._result.status_code}")

            except Exception as ex:
                last_ex = ex
                print(f"Error query:", ex)

            import time

            time.sleep(self._delay)

        self._b = None

        if last_ex is not None:
            self._result = last_ex


class ThreadRequests(AuthRequestsMixin, AuthCredentialsMixin):
    def __init__(
        self,
        credentials: AuthCredentialsMixin,
    ):
        super().__init__()
        self._c = credentials

    @property
    def credentials(self) -> dict: return self._c.credentials

    def inject_credentials(self, **kwarks) -> dict[str, any]:
        return self._c.inject_credentials(**kwarks)

    def reset_credentials(self):
        return self._c.reset_credentials()
    
    def url_credentials(self) -> dict[str, str]:
        return self._c.url_credentials()
    
    def get(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return self(get, *args, **kwargs)

    def post(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return self(post, *args, **kwargs)

    def put(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return self(put, *args, **kwargs)

    def patch(
        self,
        *args,
        **kwargs,
    ):
        return self(patch, *args, **kwargs)

    def delete(
        self,
        *args,
        **kwargs,
    ) -> Response:
        return self(delete, *args, **kwargs)

    def __call__(
        self,
        request_method,
        url: str,
        retries: int = 1,
        error_delay: float = 3,
        wait_result: bool = True,
        check_responce: Optional[Callable[[Response], bool]] = None,
        **kwarks,
    ) -> Response | None:
        try:
            return ThreadRequestTask(self._c).start(
                request_method,
                url=url,
                retries=retries,
                error_delay=error_delay,
                wait_result=wait_result,
                check_responce=check_responce,
                **kwarks,
            )
        except Exception as ex:
            import traceback

            print(ex, traceback.format_exc())

            if wait_result:
                raise ex
