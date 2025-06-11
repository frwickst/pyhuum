from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig


@dataclass
class HuumStatus(DataClassDictMixin):
    code: int
    text: str


@dataclass
class HuumConfig(DataClassDictMixin):
    code: int
    text: str


@dataclass
class HuumSteamerError(DataClassDictMixin):
    code: int
    text: str


@dataclass
class SaunaConfig(DataClassDictMixin):
    child_lock: str
    max_heating_time: int
    min_heating_time: int
    max_temp: int
    min_temp: int
    max_timer: int
    min_timer: int

    class Config(BaseConfig):
        aliases = {
            "child_lock": "childLock",
            "max_heating_time": "maxHeatingTime",
            "min_heating_time": "minHeatingTime",
            "max_temp": "maxTemp",
            "min_temp": "minTemp",
            "max_timer": "maxTimer",
            "min_timer": "minTimer",
        }


@dataclass
class HuumStatusResponse(DataClassDictMixin):
    status: int
    door_closed: bool
    temperature: int
    sauna_name: str
    target_temperature: int | None = None
    start_date: int | None = None
    end_date: int | None = None
    duration: int | None = None
    config: int | None = None
    steamer_error: int | None = None
    payment_end_date: str | None = None
    is_private: bool | None = None
    show_modal: bool | None = None
    light: int | None = None
    target_humidity: int | None = None
    humidity: int | None = None
    remote_safety_state: str | None = None
    sauna_config: SaunaConfig | None = None

    class Config(BaseConfig):
        aliases = {
            "status": "statusCode",
            "door_closed": "door",
            "target_temperature": "targetTemperature",
            "start_date": "startDate",
            "end_date": "endDate",
            "steamer_error": "steamerError",
            "payment_end_date": "paymentEndDate",
            "is_private": "isPrivate",
            "show_modal": "showModal",
            "target_humidity": "targetHumidity",
            "remote_safety_state": "remoteSafetyState",
            "sauna_config": "saunaConfig",
            "sauna_name": "saunaName",
        }
