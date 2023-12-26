from typing import Any
from unittest import TestCase
from unittest.mock import patch

import pytest

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
    expected_result = HuumStatusResponse(**idle_status_response)
    mock_request.return_value = MockResponse(idle_status_response, 200)

    huum = Huum("test", "test")
    await huum.open_session()
    response = await huum.status()

    TestCase().assertDictEqual(response.model_dump(), expected_result.model_dump())


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
    expected_result = HuumStatusResponse(**heating_status_response)
    mock_request.return_value = MockResponse(heating_status_response, 200)

    huum = Huum("test", "test")
    await huum.open_session()
    response = await huum.status()

    TestCase().assertDictEqual(response.model_dump(), expected_result.model_dump())


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
    expected_result = HuumStatusResponse(**heating_stop_response)
    mock_request.return_value = MockResponse(heating_stop_response, 200)

    huum = Huum("test", "test")
    await huum.open_session()
    response = await huum.turn_off()

    TestCase().assertDictEqual(response.model_dump(), expected_result.model_dump())


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
    expected_result = HuumStatusResponse(**heating_start_response)
    mock_request.return_value = MockResponse(heating_start_response, 200)

    huum = Huum("test", "test")
    await huum.open_session()
    response = await huum.turn_on(75)

    TestCase().assertDictEqual(response.model_dump(), expected_result.model_dump())
