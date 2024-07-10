from typing import Any
from unittest import TestCase
from unittest.mock import patch

import pytest

from huum.exceptions import BadRequest, Forbidden, NotAuthenticated, RequestError
from huum.huum import Huum
from huum.schemas import HuumStatusResponse
from tests.utils import MockResponse


@pytest.mark.asyncio
@patch("aiohttp.ClientSession._request")
async def test_status_idle(mock_request: Any) -> None:
    idle_status_response = {
        "maxHeatingTime": "3",
        "statusCode": 232,
        "door": True,
        "paymentEndDate": None,
        "temperature": "21",
    }
    expected_result = HuumStatusResponse.from_dict(idle_status_response)
    mock_request.return_value = MockResponse(idle_status_response, 200)

    huum = Huum("test", "test")
    await huum.open_session()
    response = await huum.status()

    TestCase().assertDictEqual(response.to_dict(), expected_result.to_dict())


@pytest.mark.asyncio
@patch("aiohttp.ClientSession._request")
async def test_status_heating(mock_request: Any) -> None:
    heating_status_response = {
        "maxHeatingTime": "3",
        "statusCode": 231,
        "door": True,
        "paymentEndDate": None,
        "temperature": "21",
        "targetTemperature": "75",
        "startDate": 1631623054,
        "endDate": 1631633854,
        "duration": 179,
    }
    expected_result = HuumStatusResponse.from_dict(heating_status_response)
    mock_request.return_value = MockResponse(heating_status_response, 200)

    huum = Huum("test", "test")
    await huum.open_session()
    response = await huum.status()

    TestCase().assertDictEqual(response.to_dict(), expected_result.to_dict())


@pytest.mark.asyncio
@patch("aiohttp.ClientSession._request")
async def test_heating_stop(mock_request: Any) -> None:
    heating_stop_response = {
        "maxHeatingTime": "3",
        "statusCode": 232,
        "door": True,
        "paymentEndDate": None,
        "temperature": "22",
        "targetTemperature": "75",
        "startDate": 1631685790,
        "endDate": 1631685790,
        "duration": 0,
    }
    expected_result = HuumStatusResponse.from_dict(heating_stop_response)
    mock_request.return_value = MockResponse(heating_stop_response, 200)

    huum = Huum("test", "test")
    await huum.open_session()
    response = await huum.turn_off()

    TestCase().assertDictEqual(response.to_dict(), expected_result.to_dict())


@pytest.mark.asyncio
@patch("aiohttp.ClientSession._request")
async def test_heating_start(mock_request: Any) -> None:
    heating_start_response = {
        "maxHeatingTime": "3",
        "statusCode": 231,
        "door": True,
        "paymentEndDate": None,
        "temperature": "22",
        "targetTemperature": "75",
        "startDate": 1631685780,
        "endDate": 1631696580,
        "duration": 180,
    }
    expected_result = HuumStatusResponse.from_dict(heating_start_response)
    mock_request.return_value = MockResponse(heating_start_response, 200)

    huum = Huum("test", "test")
    await huum.open_session()
    response = await huum.turn_on(75)

    TestCase().assertDictEqual(response.to_dict(), expected_result.to_dict())


@pytest.mark.parametrize(
    (
        "status_code",
        "exception",
    ),
    [
        (
            400,
            BadRequest,
        ),
        (
            401,
            NotAuthenticated,
        ),
        (
            403,
            Forbidden,
        ),
        (
            500,
            RequestError,
        ),
    ],
)
@pytest.mark.asyncio
@patch("aiohttp.ClientSession._request")
async def test_error_codes(mock_request: Any, status_code: int, exception: type[Exception]) -> None:
    mock_request.return_value = MockResponse({}, status_code)

    huum = Huum("test", "test")
    await huum.open_session()
    with pytest.raises(exception):
        await huum.status()
