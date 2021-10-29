from typing import Any
from unittest.mock import patch

import aiohttp
import pytest

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
    with pytest.raises(ValueError):
        Huum()


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
async def test_bad_response_code(mock_request: Any) -> None:
    test_response_text = "__test string__"
    mock_request.return_value = MockResponse({}, 400, test_response_text)

    huum = Huum("test", "test")
    await huum.open_session()
    with pytest.raises(aiohttp.ClientError) as exception:
        await huum.status()
    assert test_response_text in str(exception.value)
