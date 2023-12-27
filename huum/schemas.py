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
class HuumStatusResponse(DataClassDictMixin):
    status: int
    door_closed: bool
    temperature: int
    max_heating_time: int
    target_temperature: int | None = None
    start_date: int | None = None
    end_date: int | None = None
    duration: int | None = None
    config: int | None = None
    steamer_error: int | None = None
    payment_end_date: int | None = None

    class Config(BaseConfig):
        aliases = {
            "status": "statusCode",
            "door_closed": "door",
            "max_heating_time": "maxHeatingTime",
            "target_temperature": "targetTemperature",
            "start_date": "startDate",
            "end_date": "endDate",
            "steamer_error": "steamerError",
            "payment_end_date": "paymentEndDate",
        }
