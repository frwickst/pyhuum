from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from requests import RequestException, Response

from huum.schemas import HuumStatusReponse
from huum.settings import settings


class HuumSession(requests.Session):
    def __init__(self, username: str, password: str) -> None:
        super().__init__()
        self.url_base = "https://api.huum.eu/action/home/"
        self.auth = (username, password)

    def request(
        self, method: str, url: Any, *args: Any, **kwargs: Any
    ) -> requests.Response:
        url = urljoin(self.url_base, url)
        return super().request(method, url, **kwargs)


class Huum:
    """
    Usage:
        # Usage with env vars
        huum = Huum()

        # Setting auth variables explicitly
        huum = Huum(username="foo", password="bar)
    """

    min_temp = 40
    max_temp = 110

    def __init__(
        self,
        username: Optional[str] = settings.huum_username,
        password: Optional[str] = settings.huum_password,
    ) -> None:
        if not username or not password:
            raise ValueError(
                "No username or password provided either by the environment nor explicitly"
            )
        self.api = HuumSession(username=username, password=password)

    def __handle_request_error(self, url: str, response: Response) -> None:
        if response.status_code != 200:
            raise RequestException(
                f"Request to {url} failed with status code {response.status_code}. {response.text}"
            )

    def __call_get(
        self, url: str, query_params: Optional[Dict[str, Any]] = None
    ) -> Any:
        if not query_params:
            query_params = {}

        response = self.api.get(url, params=query_params)
        self.__handle_request_error(url, response)
        return response.json()

    def __call_post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Any:
        if not data:
            data = {}

        response = self.api.post(url, json=data)
        self.__handle_request_error(url, response)
        return response.json()

    def status(self) -> HuumStatusReponse:
        url = "status"

        json_response = self.__call_get(url)
        return HuumStatusReponse(**json_response)

    def turn_on(self, temperature: int) -> HuumStatusReponse:
        if temperature not in range(self.min_temp, self.max_temp):
            raise ValueError(
                f"Temperature '{temperature}' must be between {self.min_temp}-{self.max_temp}"
            )

        url = "start"
        data = {"targetTemperature": temperature}

        json_response = self.__call_post(url, data=data)
        return HuumStatusReponse(**json_response)

    def turn_off(self) -> HuumStatusReponse:
        url = "stop"

        json_response = self.__call_post(url)
        return HuumStatusReponse(**json_response)
