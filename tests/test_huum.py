from typing import Any
from unittest.mock import patch

import aiohttp
import pytest

from huum.const import SaunaStatus
from huum.exceptions import SafetyException
from huum.huum import Huum
from tests.utils import MockResponse


@pytest.mark.asyncio
async def test_with_session() -> None:
    session = aiohttp.ClientSession()
    Huum("test", "test", session)


@pytest.mark.asyncio
async def test_closing_session() -> None:
    huum = Huum("test", "test")
    await huum.open_session()
    assert huum.session._connector is not None
    await huum.close_session()
    assert huum.session._connector is None


@pytest.mark.asyncio
async def test_no_auth() -> None:
    with pytest.raises(TypeError):
        Huum()  # type: ignore


@pytest.mark.asyncio
@patch("aiohttp.ClientSession._request")
async def test_door_open_on_check(mock_request: Any) -> None:
    response = {
        "statusCode": SaunaStatus.ONLINE_NOT_HEATING,
        "door": False,
        "temperature": 80,
        "maxHeatingTime": 180,
        "saunaName": "test",
    }
    mock_request.return_value = MockResponse(response, 200)

    huum = Huum("test", "test")
    await huum.open_session()
    with pytest.raises(SafetyException):
        await huum._check_door()


@pytest.mark.asyncio
@patch("aiohttp.ClientSession._request")
async def test_bad_temperature_value(mock_request: Any) -> None:
    mock_request.return_value = MockResponse({}, 400)

    huum = Huum("test", "test")
    await huum.open_session()
    with pytest.raises(ValueError):
        await huum.turn_on(temperature=200)


@pytest.mark.asyncio
@patch("aiohttp.ClientSession._request")
async def test_set_temperature_turn_on(mock_request: Any) -> None:
    response = {
        "statusCode": SaunaStatus.ONLINE_NOT_HEATING,
        "door": True,
        "temperature": 80,
        "maxHeatingTime": 180,
        "saunaName": "test",
    }
    mock_request.return_value = MockResponse(response, 200)

    huum = Huum("test", "test")
    await huum.open_session()
    result_turn_on = await huum.turn_on(temperature=80)
    result_set_temperature = await huum.set_temperature(temperature=80)

    assert result_turn_on == result_set_temperature
