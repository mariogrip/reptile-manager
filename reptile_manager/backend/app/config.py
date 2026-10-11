import re
from pathlib import Path
from pydantic_settings import BaseSettings

def _addon_version() -> str:
    """Read the version from the add-on's config.yaml (single source of truth)."""
    here = Path(__file__).resolve()
    # Docker image: /app/config.yaml; repo checkout: reptile_manager/config.yaml
    for path in (here.parents[1] / "config.yaml", here.parents[2] / "config.yaml"):
        try:
            m = re.search(r'^version:\s*["\']?([^"\'\s]+)', path.read_text(), re.M)
            if m:
                return m.group(1)
        except OSError:
            continue
    return "dev"

APP_VERSION = _addon_version()

class Settings(BaseSettings):
    database_url: str = "postgresql://reptile:reptilepass@db:5432/reptiledb"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    first_admin_username: str = "admin"
    first_admin_password: str = "admin123"

    class Config:
        env_file = ".env"

settings = Settings()
