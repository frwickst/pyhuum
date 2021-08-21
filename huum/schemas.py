from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

status_code_texts = {
    230: "offline",
    231: "online and heating",
    232: "online but not heating",
    233: "being used by another user and is locked",
    400: "emergency stop",
}

config_code_texts = {
    1: "Configured to user light system",
    2: "Configured to use steamer system",
    3: "Configured to use both light and steamer systems",
}

steamer_code_texts = {1: "No water in steamer, steamer system not allowed to start"}


class HuumStatus(BaseModel):
    code: int
    text: str


class HuumConfig(BaseModel):
    code: int
    text: str


class HuumSteamerError(BaseModel):
    code: int
    text: str


class HuumStatusReponse(BaseModel):
    status: int = Field(alias="statusCode")
    door_closed: bool = Field(alias="door")
    temperature: str
    max_heating_time: int = Field(alias="maxHeatingTime")
    target_temperature: Optional[str] = Field(alias="targetTemperature")
    start_date: Optional[datetime] = Field(alias="startDate")
    end_date: Optional[datetime] = Field(alias="endDate")
    duration: Optional[int] = Field(alias="")
    config: Optional[int]
    streamer_error: Optional[int] = Field(alias="streamerError")
    payment_end_date: Optional[datetime] = Field(alias="paymentEndDate")
