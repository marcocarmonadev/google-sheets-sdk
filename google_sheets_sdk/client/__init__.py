from dataclasses import InitVar, dataclass, field
from typing import ClassVar

from httpx import AsyncClient, HTTPStatusError

from google_sheets_sdk.core import Settings, models


@dataclass
class Client:
    _BASE_URL: ClassVar[str] = "https://sheets.googleapis.com/"

    _http_client: AsyncClient
    _token: models.Token = field(
        init=False,
    )
    settings: InitVar[Settings]

    def __post_init__(
        self,
        settings: Settings,
    ):
        self._token = models.Token(
            email=settings.CLIENT_EMAIL,
            base_url=self._BASE_URL,
            scope=settings.SCOPE.unicode_string(),
            private_key=settings.PRIVATE_KEY.replace(r"\n", "\n"),
            private_key_id=settings.PRIVATE_KEY_ID,
        )

    async def batch_clear_values(
        self,
        spreadsheet_id: models.SpreadsheetId,
        ranges: list[models.Range],
    ) -> None:
        try:
            response = await self._http_client.post(
                url=f"{self._BASE_URL}v4/spreadsheets/{spreadsheet_id}/values:batchClear",
                json={
                    "ranges": ranges,
                },
                headers={
                    "Authorization": f"Bearer {self._token.encoded}",
                },
            )
            response.raise_for_status()
        except HTTPStatusError as exc:
            raise exc

    async def batch_update_values(
        self,
        spreadsheet_id: models.SpreadsheetId,
        sheets: list[models.Sheet],
    ) -> models.BatchUpdateValuesResponse:
        try:
            response = await self._http_client.post(
                url=f"{self._BASE_URL}v4/spreadsheets/{spreadsheet_id}/values:batchUpdate",
                json={
                    "valueInputOption": "USER_ENTERED",
                    "data": [
                        sheet.model_dump(
                            mode="json",
                        )
                        for sheet in sheets
                    ],
                },
                headers={
                    "Authorization": f"Bearer {self._token.encoded}",
                },
            )
            response.raise_for_status()
        except HTTPStatusError as exc:
            raise exc
        else:
            return models.BatchUpdateValuesResponse(**response.json())
