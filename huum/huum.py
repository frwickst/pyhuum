from typing import Any, Optional
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientResponse

from huum.exceptions import (
    BadRequest,
    Forbidden,
    NotAuthenticated,
    RequestError,
    SafetyException,
)
from huum.schemas import HuumStatusResponse

API_BASE = "https://sauna.huum.eu/action/"
API_HOME_BASE = f"{API_BASE}/home/"


class Huum:
    """
    Usage:
        # Usage with env vars
        huum = Huum()

        # Setting auth variables explicitly
        huum = Huum(username="foo", password="bar")

        # If you don't have an existing aiohttp session
        # then run `open_session()` after initializing
        huum.open_session()

        # Turn on the sauna
        huum.turn_on(80)
    """

    min_temp = 40
    max_temp = 110

    session: aiohttp.ClientSession

    def __init__(
        self,
        username: str,
        password: str,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        if session:
            self.session = session

        self.auth = aiohttp.BasicAuth(username, password)

    async def _check_door(self) -> None:
        """
        Check if the door is closed, if not, raise an exception
        """
        status = await self.status()
        if not status.door_closed:
            raise SafetyException("Can not start sauna when door is open")

    async def _make_call(self, method: str, url: str, json: Any | None = None) -> ClientResponse:
        call_args = {
            "url": url,
            "auth": self.auth,
        }
        if json:
            call_args["json"] = json

        call_request = getattr(self.session, method.lower())

        response: ClientResponse = await call_request(**call_args)

        try:
            response.raise_for_status()
        except Exception as err:
            match response.status:
                case 400:
                    raise BadRequest("Bad request") from err
                case 401:
                    raise NotAuthenticated("Not authenticated") from err
                case 403:
                    raise Forbidden("Forbidden") from err
            raise RequestError() from err

        return response

    async def turn_on(self, temperature: int, safety_override: bool = False) -> HuumStatusResponse:
        """
        Turns on the sauna at a given temperature

        Args:
            temperature: Target temperature to set the sauna to
            safety_override: If False, check if door is close before turning on the sauna

        Returns:
            A `HuumStatusResponse` from the Huum API
        """
        if temperature not in range(self.min_temp, self.max_temp):
            raise ValueError(
                f"Temperature '{temperature}' must be between {self.min_temp}-{self.max_temp}"
            )

        if not safety_override:
            await self._check_door()

        url = urljoin(API_HOME_BASE, "start")
        data = {"targetTemperature": temperature}

        response = await self._make_call("post", url, json=data)
        json_data = await response.json()

        return HuumStatusResponse.from_dict(json_data)

    async def turn_off(self) -> HuumStatusResponse:
        """
        Turns off the sauna

        Returns:
            A `HuumStatusResponse` from the Huum API

        """
        url = urljoin(API_HOME_BASE, "stop")

        response = await self._make_call("post", url)
        json_data = await response.json()

        return HuumStatusResponse.from_dict(json_data)

    async def set_temperature(
        self, temperature: int, safety_override: bool = False
    ) -> HuumStatusResponse:
        """
        Alias for turn_on as Huum does not expose an explicit "set_temperature" endpoint

        Implementation choice: Yes, aliasing can be done by simply assigning
        set_temperature = turn_on, however this will not create documentation,
        makes the code harder to read and is generally seen as non-pythonic.

        Args:
            temperature: Target temperature to set the sauna to
            safety_override: If False, check if door is close before turning on the sauna

        Returns:
            A `HuumStatusResponse` from the Huum API
        """
        return await self.turn_on(temperature, safety_override)

    async def status(self) -> HuumStatusResponse:
        """
        Get the status of the Sauna

        Returns:
            A `HuumStatusResponse` from the Huum API
        """
        url = urljoin(API_HOME_BASE, "status")

        response = await self._make_call("get", url)
        json_data = await response.json()

        return HuumStatusResponse.from_dict(json_data)

    async def toggle_light(self) -> HuumStatusResponse:
        """
        Toggles the light/fan on a Sauna

        Returns:
            A `HuumStatusResponse` from the Huum API
        """
        url = urljoin(API_HOME_BASE, "light")

        response = await self._make_call("get", url)
        json_data = await response.json()

        return HuumStatusResponse.from_dict(json_data)

    async def open_session(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close_session(self) -> None:
        await self.session.close()
