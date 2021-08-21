from typing import Any


class MockResponse:
    def __init__(
        self, json_data: dict[str, Any], status_code: int, text: str = ""
    ) -> None:
        self.json_data = json_data
        self.status_code = status_code
        self.text = text

    def json(self) -> dict[str, Any]:
        return self.json_data
