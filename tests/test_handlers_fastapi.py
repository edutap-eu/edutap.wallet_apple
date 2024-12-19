# pylint: disable=unused-argument

# pylint: disable=redefined-outer-name

from edutap.wallet_apple.models import handlers
from importlib import metadata
from importlib.metadata import entry_points
from importlib.metadata import EntryPoint

import pytest


try:
    from edutap.wallet_apple.handlers.fastapi import router
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    have_fastapi = True
except ImportError:
    have_fastapi = False
    raise


class TestPassRegistration:
    async def register_pass(
        self,
        device_id: str,
        pass_type_id: str,
        serial_number: str,
        push_token: handlers.PushToken,
    ) -> None: ...

    async def unregister_pass(
        self, device_id: str, pass_type_id: str, serial_number: str
    ) -> None: ...


class TestPassDataAcquisition:
    async def get_pass_data(self, pass_id: str) -> handlers.PassData:
        return None

    async def get_push_tokens(
        self, device_type_id: str | None, pass_type_id: str, serial_number: str
    ) -> list[handlers.PushToken]:
        return []

    def test_get_update_serial_numbers(self):
        pass

    async def get_update_serial_numbers(
        self, device_type_id: str, pass_type_id: str, last_updated: str
    ) -> handlers.SerialNumbers:
        return handlers.SerialNumbers(
            serialNumers=["1234"], lastUpdated="2021-09-01T12:00:00Z"
        )


@pytest.fixture
def entrypoints_testing(monkeypatch):
    eps = {
        "edutap.wallet_apple.plugins": [
            EntryPoint(
                name="PassRegistration",
                value="test_handlers_fastapi:TestPassRegistration",
                group="edutap.wallet_apple.handlers.fastapi.router",
            ),
            EntryPoint(
                name="PassDataAcquisition",
                value="test_handlers_fastapi:TestPassDataAcquisition",
                group="edutap.wallet_apple.handlers.fastapi.router",
            ),
        ]
    }

    def mock_entry_points(group: str):
        return eps.get(group, [])

    monkeypatch.setattr(metadata, "entry_points", mock_entry_points)
    return mock_entry_points


def test_entrypoints(entrypoints_testing):
    from edutap.wallet_apple.plugins import get_pass_data_acquisitions
    from edutap.wallet_apple.plugins import get_pass_registrations

    pr = get_pass_registrations()
    pd = get_pass_data_acquisitions()
    print(pr)


@pytest.mark.skipif(not have_fastapi, reason="fastapi not installed")
def test_get_pass(entrypoints_testing):
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    response = client.get("/apple_update_service/v1/passes/1234/1234")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
