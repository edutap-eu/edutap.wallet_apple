from edutap.wallet_apple.settings import Settings
from pathlib import Path

import conftest


def test_settings_via_env_dict(monkeypatch):

    # Set the environment variables
    monkeypatch.delenv("EDUTAP_WALLET_APPLE_ROOT_DIR", raising=False)
    monkeypatch.delenv("EDUTAP_WALLET_APPLE_CERT_DIR", raising=False)
    monkeypatch.setenv(
        "EDUTAP_WALLET_APPLE_ROOT_DIR",
        str(conftest.cwd / "data"),
    )
    settings = Settings()
    assert settings.root_dir == conftest.cwd / "data"
    assert settings.cert_dir == conftest.cwd / "data" / "certs"

    # certificates dir defined relative to root dir
    monkeypatch.setenv(
        "EDUTAP_WALLET_APPLE_CERT_DIR_RELATIVE",
        "certs/private",
    )
    settings = Settings()
    assert settings.root_dir == conftest.cwd / "data"
    assert settings.cert_dir == conftest.cwd / "data" / "certs/private"
    assert (
        settings.private_key == conftest.cwd / "data" / "certs/private" / "private.key"
    )
    assert (
        settings.get_certificate_path("pass.demo.lmu.de")
        == conftest.cwd / "data" / "certs/private" / "certificate-pass.demo.lmu.de.pem"
    )
    assert (
        settings.wwdr_certificate
        == conftest.cwd / "data" / "certs/private" / "wwdr_certificate.pem"
    )

    # assert settings.key.exists()

    # certificates dir defined absolute
    monkeypatch.setenv(
        "EDUTAP_WALLET_APPLE_CERT_DIR",
        "/certificates",
    )
    settings = Settings()
    assert settings.root_dir == conftest.cwd / "data"
    assert settings.cert_dir == Path("/certificates")
    assert settings.private_key == Path("/certificates/private.key")


def test_settings_via_env_file():
    env_file = conftest.cwd / "data" / ".env-testing"
    assert env_file.exists()

    settings = Settings(_env_file=env_file)
    assert settings.cert_dir == conftest.cwd / "data" / "certs" / "private"
    # assert settings.cert_dir.exists()
