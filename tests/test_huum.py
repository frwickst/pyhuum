from typing import Any
from unittest.mock import patch

import pytest
from requests import RequestException

from huum.huum import Huum
from tests.utils import MockResponse


def test_no_auth() -> None:
    with pytest.raises(ValueError):
        Huum()


@patch("requests.Session.request")
def test_bad_temperature_value(mock_request: Any) -> None:
    mock_request.return_value = MockResponse({}, 400)

    huum = Huum("test", "test")
    with pytest.raises(ValueError):
        huum.turn_on(temperature=200)


@patch("requests.Session.request")
def test_bad_response_code(mock_request: Any) -> None:
    test_response_text = "__test string__"
    mock_request.return_value = MockResponse({}, 400, test_response_text)

    huum = Huum("test", "test")
    with pytest.raises(RequestException) as exception:
        huum.status()
    assert test_response_text in str(exception.value)
