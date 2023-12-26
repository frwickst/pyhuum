from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class HuumStatus(BaseModel):
    code: int
    text: str


class HuumConfig(BaseModel):
    code: int
    text: str


class HuumSteamerError(BaseModel):
    code: int
    text: str


class HuumStatusResponse(BaseModel):
    status: int = Field(alias="statusCode")
    door_closed: bool = Field(alias="door")
    temperature: int
    max_heating_time: int = Field(alias="maxHeatingTime")
    target_temperature: Optional[
        Annotated[int, Field(alias="targetTemperature")]
    ] = None
    start_date: Optional[Annotated[datetime, Field(alias="startDate")]] = None
    end_date: Optional[Annotated[datetime, Field(alias="endDate")]] = None
    duration: Optional[Annotated[int, Field(alias="")]] = None
    config: Optional[int] = None
    streamer_error: Annotated[Optional[int], Field(alias="streamerError")] = None
    payment_end_date: Optional[
        Annotated[datetime, Field(alias="paymentEndDate")]
    ] = None
