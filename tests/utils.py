from typing import Any


class MockResponse:
    def __init__(
        self, json_data: dict[str, Any], status_code: int, text: str = ""
    ) -> None:
        self._json = json_data
        self._text = text

        self.status = status_code

    async def json(self) -> dict[str, Any]:
        return self._json
