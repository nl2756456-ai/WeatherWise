"""
config.py

Central place for every constant and setting WeatherWise needs.
No business logic lives here - only values.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load environment variables from the .env file into os.environ
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"
CACHE_DIR: Path = DATA_DIR / "cache"
ASSETS_DIR: Path = BASE_DIR / "assets"

FAVORITES_FILE: Path = DATA_DIR / "favorites.json"
SETTINGS_FILE: Path = DATA_DIR / "settings.json"
HISTORY_FILE: Path = DATA_DIR / "history.json"

# ---------------------------------------------------------------------------
# API configuration
# ---------------------------------------------------------------------------
OPENWEATHER_API_KEY: str | None = os.getenv("OPENWEATHER_API_KEY")

OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
OPENWEATHER_GEO_URL: str = "https://api.openweathermap.org/geo/1.0"

# ---------------------------------------------------------------------------
# Default application settings
# ---------------------------------------------------------------------------
DEFAULT_TEMP_UNIT: str = "metric"   # "metric" = Celsius, "imperial" = Fahrenheit
DEFAULT_WIND_UNIT: str = "kmh"      # "kmh" or "mph"
DEFAULT_THEME: str = "dark"         # "dark" or "light"
DEFAULT_LANGUAGE: str = "en"

AUTO_REFRESH_MINUTES: int = 10

# ---------------------------------------------------------------------------
# Startup validation
# ---------------------------------------------------------------------------
def validate_config() -> None:
    """
    Check that required configuration is present before the app starts.
    Raises a clear error instead of letting the app fail mysteriously later.
    """
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "your_api_key_here":
        raise RuntimeError(
            "Missing OpenWeatherMap API key. "
            "Copy .env.example to .env and add your real key."
        )
