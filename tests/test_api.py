import unittest
from typing import Any, Callable
from unittest.mock import patch

from huum.huum import Huum
from huum.schemas import HuumStatusReponse
from tests.utils import MockResponse


class TestHuum(unittest.TestCase):
    def setup_method(self, test_method: Callable[[Any], Any]) -> None:
        self.mock_request_patcher = patch("requests.Session.request")
        self.mock_request = self.mock_request_patcher.start()

        self.huum = Huum("test", "test")

    def teardown_method(self, test_method: Callable[[Any], Any]) -> None:
        self.mock_request_patcher.stop()

    def test_status_idle(self) -> None:
        idle_status_response = {
            "maxHeatingTime": "3",
            "statusCode": 232,
            "door": True,
            "paymentEndDate": None,
            "temperature": "21",
        }
        expected_result = HuumStatusReponse(**idle_status_response)
        self.mock_request.return_value = MockResponse(idle_status_response, 200)

        self.huum = Huum("test", "test")
        response = self.huum.status()

        self.assertDictEqual(response.dict(), expected_result.dict())

    def test_status_heating(self) -> None:
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
        expected_result = HuumStatusReponse(**heating_status_response)
        self.mock_request.return_value = MockResponse(heating_status_response, 200)

        response = self.huum.status()

        self.assertDictEqual(response.dict(), expected_result.dict())

    def test_heating_start(self) -> None:
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
        expected_result = HuumStatusReponse(**heating_start_response)
        self.mock_request.return_value = MockResponse(heating_start_response, 200)

        response = self.huum.turn_on(75)

        self.assertDictEqual(response.dict(), expected_result.dict())

    def test_heating_stop(self) -> None:
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
        expected_result = HuumStatusReponse(**heating_stop_response)
        self.mock_request.return_value = MockResponse(heating_stop_response, 200)

        response = self.huum.turn_off()

        self.assertDictEqual(response.dict(), expected_result.dict())
