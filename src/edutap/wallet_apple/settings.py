from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


ROOT_DIR = Path(__file__).parent.parent.parent.parent.resolve()


class AppleWalletSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="edutap_wallet_apple_",
        case_sensitive=False,
        extra="ignore",
    )
    key: Path = ROOT_DIR / "private.key"
    certificate: Path = ROOT_DIR / "certificate.pem"
    wwdr_certificate: Path = ROOT_DIR / "wwdr_certificate.pem"
    password: str | None = None

    pass_type_identifier: str | None = None
    team_identifier: str | None = None
