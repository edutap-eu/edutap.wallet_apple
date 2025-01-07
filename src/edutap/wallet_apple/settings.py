from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


ROOT_DIR = Path(__file__).parents[3].resolve()


class Settings(BaseSettings):
    """
    Settings class for the edutap wallet apple application.
    """

    model_config = SettingsConfigDict(
        env_prefix="EDUTAP_WALLET_APPLE_",
        case_sensitive=False,
        env_file=".env",
        # env_file_encoding="utf-8",
        extra="allow",
    )
    root_dir: Path = Field(default_factory=lambda dd: dd.get("root_dir", ROOT_DIR))
    cert_dir_relative: str = "certs"
    """Relative path to the root directory, can be overridden
    by `cert_dir`"""
    cert_dir: Path = Field(
        default_factory=lambda dd: dd["root_dir"] / dd["cert_dir_relative"]
    )
    """directory where the certificates and keys are stored"""
    private_key: Path = Field(default_factory=lambda dd: dd["cert_dir"] / "private.key")
    """Path to the private key file in PEM format"""
    certificate: Path = Field(
        default_factory=lambda dd: dd["cert_dir"] / "certificate.pem"
    )
    """Path to the Apple certificate file in PEM format"""
    wwdr_certificate: Path = Field(
        default_factory=lambda dd: dd["cert_dir"] / "wwdr_certificate.pem"
    )
    """Path to the Apple WWDR certificate file in PEM format"""

    https_port: int = 443
    """Port for the HTTPS server"""
    domain: str = "localhost"
    """Domain name for the HTTPS server"""

    password: str | None = None

    pass_type_identifier: str | None = None
    team_identifier: str | None = None
