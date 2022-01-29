from enum import IntEnum
from typing import Dict


class SaunaStatus(IntEnum):
    OFFLINE = 230
    ONLINE_HEATING = 231
    ONLINE_NOT_HEATING = 232
    LOCKED = 233
    EMERGENCY_STOP = 400


STATUS_CODE_TEXTS: Dict[int, str] = {
    SaunaStatus.OFFLINE: "offline",
    SaunaStatus.ONLINE_HEATING: "online and heating",
    SaunaStatus.ONLINE_NOT_HEATING: "online but not heating",
    SaunaStatus.LOCKED: "being used by another user and is locked",
    SaunaStatus.EMERGENCY_STOP: "emergency stop",
}

CONFIG_CODE_TEXTS: Dict[int, str] = {
    1: "Configured to user light system",
    2: "Configured to use steamer system",
    3: "Configured to use both light and steamer systems",
}

STEAMER_CODE_TEXTS: Dict[int, str] = {
    1: "No water in steamer, steamer system not allowed to start"
}
