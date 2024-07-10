from typing import Any

from aiohttp import ClientResponseError


class MockResponse:
    def __init__(self, json_data: dict[str, Any], status_code: int, text: str = "") -> None:
        self._json = json_data
        self._text = text

        self.status = status_code

    async def json(self) -> dict[str, Any]:
        return self._json

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise ClientResponseError(
                None,  # type: ignore
                None,  # type: ignore
                status=self.status,
                message="Bad Request",
                headers=None,
            )
