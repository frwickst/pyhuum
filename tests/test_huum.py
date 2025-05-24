from typing import Any
from unittest.mock import patch

import aiohttp
import pytest

from huum.const import SaunaStatus
from huum.exceptions import SafetyException
from huum.huum import Huum
from huum.schemas import HuumStatusResponse
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
@patch("huum.huum.Huum.status")
@patch("huum.huum.Huum.turn_off")
async def test_status_from_status_or_stop(mock_huum_turn_off: Any, mock_huum_status: Any) -> None:
    mock_huum_status.return_value = HuumStatusResponse.from_dict(
        {
            "statusCode": SaunaStatus.ONLINE_NOT_HEATING,
            "door": True,
            "temperature": 80,
            "maxHeatingTime": 1337,
        }
    )
    mock_huum_turn_off.return_value = HuumStatusResponse.from_dict(
        {
            "statusCode": SaunaStatus.ONLINE_NOT_HEATING,
            "door": True,
            "temperature": 90,
            "maxHeatingTime": 1337,
        }
    )
    huum = Huum("test", "test")
    await huum.open_session()

    status = await huum.status_from_status_or_stop()

    assert status.temperature == 90


@pytest.mark.asyncio
@patch("aiohttp.ClientSession._request")
async def test_door_open_on_check(mock_request: Any) -> None:
    response = {
        "statusCode": SaunaStatus.ONLINE_NOT_HEATING,
        "door": False,
        "temperature": 80,
        "maxHeatingTime": 180,
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
    }
    mock_request.return_value = MockResponse(response, 200)

    huum = Huum("test", "test")
    await huum.open_session()
    result_turn_on = await huum.turn_on(temperature=80)
    result_set_temperature = await huum.set_temperature(temperature=80)

    assert result_turn_on == result_set_temperature


@pytest.mark.asyncio
class TestHuumFahrenheitInput:
    @pytest.fixture
    async def huum_fixture(self) -> Huum:
        huum_instance = Huum("test_user", "test_pass")
        await huum_instance.open_session()
        # Mock a successful, door-closed status for safety checks
        status_response_dict = {
            "statusCode": SaunaStatus.ONLINE_HEATING,
            "door": True,
            "temperature": 60,
            "maxHeatingTime": 180,
            "targetTemperature": 80,
        }
        # Patch _make_call for the _check_door method if it's called separately
        # For turn_on, the main _make_call mock will handle the start command
        # For simplicity, we assume _check_door might use its own status call or reuse the main one
        # For these tests, we primarily care about the payload to "start"
        return huum_instance

    async def mock_successful_turn_on_response(self, temperature: int) -> HuumStatusResponse:
        return HuumStatusResponse.from_dict(
            {
                "statusCode": SaunaStatus.ONLINE_HEATING,
                "door": True,
                "temperature": temperature - 5, # Simulate current temp being slightly less
                "maxHeatingTime": 180,
                "targetTemperature": temperature,
            }
        )

    @patch("huum.huum.Huum._make_call")
    async def test_turn_on_fahrenheit_conversion_212F_to_100C(
        self, mock_make_call: Any, huum_fixture: Huum
    ) -> None:
        """Test 212°F converts to 100°C and is used in API call."""
        mock_make_call.return_value = await self.mock_successful_turn_on_response(100)

        await huum_fixture.turn_on(temperature=212, is_fahrenheit=True)

        # Assert _make_call was called with the correct Celsius temperature
        # The first call might be to _check_door -> status, the second to "start"
        # We need to find the call to "start"
        found_start_call = False
        for call_args in mock_make_call.call_args_list:
            if "start" in call_args.args[1]: # url is the second positional arg to _make_call
                assert call_args.kwargs["json"]["targetTemperature"] == 100
                found_start_call = True
                break
        assert found_start_call, "The 'start' API endpoint was not called."


    @patch("huum.huum.Huum._make_call")
    async def test_turn_on_fahrenheit_valid_min_104F_to_40C(
        self, mock_make_call: Any, huum_fixture: Huum
    ) -> None:
        """Test 104°F (40°C) is accepted."""
        mock_make_call.return_value = await self.mock_successful_turn_on_response(40)
        await huum_fixture.turn_on(temperature=104, is_fahrenheit=True)
        
        found_start_call = False
        for call_args in mock_make_call.call_args_list:
            if "start" in call_args.args[1]:
                assert call_args.kwargs["json"]["targetTemperature"] == 40
                found_start_call = True
                break
        assert found_start_call

    @patch("huum.huum.Huum._make_call")
    async def test_turn_on_fahrenheit_valid_max_230F_to_110C(
        self, mock_make_call: Any, huum_fixture: Huum
    ) -> None:
        """Test 230°F (110°C) is accepted."""
        mock_make_call.return_value = await self.mock_successful_turn_on_response(110)
        await huum_fixture.turn_on(temperature=230, is_fahrenheit=True)

        found_start_call = False
        for call_args in mock_make_call.call_args_list:
            if "start" in call_args.args[1]:
                assert call_args.kwargs["json"]["targetTemperature"] == 110
                found_start_call = True
                break
        assert found_start_call

    @patch("huum.huum.Huum._make_call") # Mock to prevent actual API call
    async def test_turn_on_fahrenheit_invalid_low_32F_to_0C(
        self, mock_make_call: Any, huum_fixture: Huum
    ) -> None:
        """Test 32°F (0°C) raises ValueError (too low)."""
        with pytest.raises(ValueError) as excinfo:
            await huum_fixture.turn_on(temperature=32, is_fahrenheit=True)
        assert "must be between 40-110" in str(excinfo.value)
        assert "Temperature '0'" in str(excinfo.value) # 0°C

    @patch("huum.huum.Huum._make_call")
    async def test_turn_on_fahrenheit_invalid_low_68F_to_20C(
        self, mock_make_call: Any, huum_fixture: Huum
    ) -> None:
        """Test 68°F (20°C) raises ValueError (too low)."""
        with pytest.raises(ValueError) as excinfo:
            await huum_fixture.turn_on(temperature=68, is_fahrenheit=True)
        assert "must be between 40-110" in str(excinfo.value)
        assert "Temperature '20'" in str(excinfo.value) # 20°C

    @patch("huum.huum.Huum._make_call")
    async def test_turn_on_fahrenheit_invalid_high_240F_to_115C(
        self, mock_make_call: Any, huum_fixture: Huum
    ) -> None:
        """Test 240°F (~115.55°C, int cast to 115°C) raises ValueError (too high)."""
        # 240°F = (240 - 32) * 5 / 9 = 208 * 5 / 9 = 1040 / 9 = 115.55... °C
        # int(115.55...) = 115
        with pytest.raises(ValueError) as excinfo:
            await huum_fixture.turn_on(temperature=240, is_fahrenheit=True)
        assert "must be between 40-110" in str(excinfo.value)
        assert "Temperature '115'" in str(excinfo.value)

    @patch("huum.huum.Huum._make_call")
    async def test_turn_on_celsius_default_80C(
        self, mock_make_call: Any, huum_fixture: Huum
    ) -> None:
        """Test 80°C with is_fahrenheit=False results in targetTemperature: 80."""
        mock_make_call.return_value = await self.mock_successful_turn_on_response(80)
        await huum_fixture.turn_on(temperature=80, is_fahrenheit=False)

        found_start_call = False
        for call_args in mock_make_call.call_args_list:
            if "start" in call_args.args[1]:
                assert call_args.kwargs["json"]["targetTemperature"] == 80
                found_start_call = True
                break
        assert found_start_call

    @patch("huum.huum.Huum._make_call")
    async def test_turn_on_celsius_no_flag_80C(
        self, mock_make_call: Any, huum_fixture: Huum
    ) -> None:
        """Test 80°C with is_fahrenheit not provided results in targetTemperature: 80."""
        mock_make_call.return_value = await self.mock_successful_turn_on_response(80)
        await huum_fixture.turn_on(temperature=80) # is_fahrenheit defaults to False

        found_start_call = False
        for call_args in mock_make_call.call_args_list:
            if "start" in call_args.args[1]:
                assert call_args.kwargs["json"]["targetTemperature"] == 80
                found_start_call = True
                break
        assert found_start_call

    @patch("huum.huum.Huum._make_call")
    async def test_set_temperature_fahrenheit_conversion_212F_to_100C(
        self, mock_make_call: Any, huum_fixture: Huum
    ) -> None:
        """Test set_temperature with 212°F converts to 100°C."""
        mock_make_call.return_value = await self.mock_successful_turn_on_response(100)
        await huum_fixture.set_temperature(temperature=212, is_fahrenheit=True)

        found_start_call = False
        for call_args in mock_make_call.call_args_list:
            if "start" in call_args.args[1]: # set_temperature calls turn_on, which calls _make_call with "start"
                assert call_args.kwargs["json"]["targetTemperature"] == 100
                found_start_call = True
                break
        assert found_start_call

    @patch("huum.huum.Huum._make_call")
    async def test_set_temperature_fahrenheit_invalid_low_32F_to_0C(
        self, mock_make_call: Any, huum_fixture: Huum
    ) -> None:
        """Test set_temperature with 32°F (0°C) raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            await huum_fixture.set_temperature(temperature=32, is_fahrenheit=True)
        assert "must be between 40-110" in str(excinfo.value)
        assert "Temperature '0'" in str(excinfo.value)

    # Need to ensure _check_door is also appropriately mocked if safety_override is False (default)
    # The huum_fixture does not currently mock the _make_call made by _check_door
    # Let's refine the fixture or mock _check_door directly in tests where it matters.

    @patch("huum.huum.Huum._check_door", new_callable=AsyncMock) # Mock _check_door
    @patch("huum.huum.Huum._make_call") # Mock the actual API call for turn_on
    async def test_turn_on_fahrenheit_with_mocked_check_door(
        self, mock_make_call: Any, mock_check_door: Any, huum_fixture: Huum
    ) -> None:
        """Test Fahrenheit conversion when _check_door is explicitly mocked."""
        mock_check_door.return_value = None # Simulate door is closed
        mock_make_call.return_value = await self.mock_successful_turn_on_response(100)

        await huum_fixture.turn_on(temperature=212, is_fahrenheit=True)
        
        mock_check_door.assert_called_once()
        mock_make_call.assert_called_once_with(
            "post", 
            "https://api.huum.eu/action/home/start", 
            json={"targetTemperature": 100}
        )

    @patch("huum.huum.Huum._check_door", new_callable=AsyncMock)
    @patch("huum.huum.Huum._make_call")
    async def test_set_temperature_fahrenheit_with_mocked_check_door(
        self, mock_make_call: Any, mock_check_door: Any, huum_fixture: Huum
    ) -> None:
        """Test set_temperature Fahrenheit conversion when _check_door is explicitly mocked."""
        mock_check_door.return_value = None
        mock_make_call.return_value = await self.mock_successful_turn_on_response(100)

        await huum_fixture.set_temperature(temperature=212, is_fahrenheit=True)
        
        mock_check_door.assert_called_once() # _check_door is called by turn_on
        mock_make_call.assert_called_once_with(
            "post",
            "https://api.huum.eu/action/home/start",
            json={"targetTemperature": 100}
        )
    
    # Test for safety_override = True
    @patch("huum.huum.Huum._check_door", new_callable=AsyncMock) # Should NOT be called
    @patch("huum.huum.Huum._make_call")
    async def test_turn_on_fahrenheit_safety_override(
        self, mock_make_call: Any, mock_check_door: Any, huum_fixture: Huum
    ) -> None:
        """Test turn_on with safety_override=True does not call _check_door."""
        mock_make_call.return_value = await self.mock_successful_turn_on_response(70) # e.g. 158F -> 70C

        await huum_fixture.turn_on(temperature=158, is_fahrenheit=True, safety_override=True)
        
        mock_check_door.assert_not_called()
        mock_make_call.assert_called_once_with(
            "post",
            "https://api.huum.eu/action/home/start",
            json={"targetTemperature": 70} 
        )
        
    # Test for set_temperature with safety_override = True
    @patch("huum.huum.Huum._check_door", new_callable=AsyncMock) # Should NOT be called
    @patch("huum.huum.Huum._make_call")
    async def test_set_temperature_fahrenheit_safety_override(
        self, mock_make_call: Any, mock_check_door: Any, huum_fixture: Huum
    ) -> None:
        """Test set_temperature with safety_override=True does not call _check_door."""
        mock_make_call.return_value = await self.mock_successful_turn_on_response(70)

        await huum_fixture.set_temperature(temperature=158, is_fahrenheit=True, safety_override=True)
        
        mock_check_door.assert_not_called()
        mock_make_call.assert_called_once_with(
            "post",
            "https://api.huum.eu/action/home/start",
            json={"targetTemperature": 70}
        )
