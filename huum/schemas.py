from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


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
    target_temperature: Optional[int] = Field(alias="targetTemperature")
    start_date: Optional[datetime] = Field(alias="startDate")
    end_date: Optional[datetime] = Field(alias="endDate")
    duration: Optional[int] = Field(alias="")
    config: Optional[int]
    streamer_error: Optional[int] = Field(alias="streamerError")
    payment_end_date: Optional[datetime] = Field(alias="paymentEndDate")
