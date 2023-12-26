from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Annotated

from mashumaro import DataClassDictMixin, field_options


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
    status: int = field(metadata=field_options(alias="statusCode"))
    door_closed: bool = field(metadata=field_options(alias="door"))
    temperature: int
    max_heating_time: int = field(metadata=field_options(alias="maxHeatingTime"))
    target_temperature: Optional[
        Annotated[int, field(metadata=field_options(alias="targetTemperature"))]
    ] = None
    start_date: Optional[
        Annotated[datetime, field(metadata=field_options(alias="startDate"))]
    ] = None
    end_date: Optional[
        Annotated[datetime, field(metadata=field_options(alias="endDate"))]
    ] = None
    duration: Optional[int] = None
    config: Optional[int] = None
    streamer_error: Annotated[
        Optional[int], field(metadata=field_options(alias="streamerError"))
    ] = None
    payment_end_date: Optional[
        Annotated[datetime, field(metadata=field_options(alias="paymentEndDate"))]
    ] = None
