from edutap.wallet_apple.settings import Settings
from pathlib import Path

import common
import os


def test_settings_via_env_dict(monkeypatch):

    # Set the environment variables
    monkeypatch.setenv(
        "EDUTAP_WALLET_APPLE_ROOT_DIR",
        str(common.cwd / "data"),
    )
    settings = Settings()
    assert settings.root_dir == common.cwd / "data"
    assert settings.cert_dir == common.cwd / "data" / "certs"

    # certificates dir defined relative to root dir
    monkeypatch.setenv(
        "EDUTAP_WALLET_APPLE_CERT_DIR_RELATIVE",
        "certs/private",
    )
    settings = Settings()
    assert settings.root_dir == common.cwd / "data"
    assert settings.cert_dir == common.cwd / "data" / "certs/private"
    assert settings.private_key == common.cwd / "data" / "certs/private" / "private.key"
    assert (
        settings.certificate
        == common.cwd / "data" / "certs/private" / "certificate.pem"
    )
    assert (
        settings.wwdr_certificate
        == common.cwd / "data" / "certs/private" / "wwdr_certificate.pem"
    )

    # assert settings.key.exists()

    # certificates dir defined absolute
    monkeypatch.setenv(
        "EDUTAP_WALLET_APPLE_CERT_DIR",
        "/certificates",
    )
    settings = Settings()
    assert settings.root_dir == common.cwd / "data"
    assert settings.cert_dir == Path("/certificates")
    assert settings.private_key == Path("/certificates/private.key")


def test_settings_via_env_file():
    env_file = common.cwd / "data" / ".env-testing"
    assert env_file.exists()

    settings = Settings(_env_file=env_file)
    assert settings.cert_dir == common.cwd / "data" / "certs" / "private"
    # assert settings.cert_dir.exists()
