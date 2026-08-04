"""
cache.py

JSON-backed persistence for favorites, recent searches, settings,
and the last successfully fetched weather (for offline fallback).
"""

import json
import logging
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger(__name__)


class JSONStore:
    """Generic helper for reading/writing a JSON file with a default value."""

    def __init__(self, path: Path, default: Any):
        self.path = path
        self.default = default
        self._ensure_exists()

    def _ensure_exists(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists() or self.path.stat().st_size == 0:
            self.write(self.default)

    def read(self) -> Any:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("Corrupt or missing JSON at %s, resetting to default.", self.path)
            self.write(self.default)
            return self.default

    def write(self, data: Any) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)


class FavoritesStore(JSONStore):
    def __init__(self):
        super().__init__(config.FAVORITES_FILE, default=[])

    def add(self, city: str, lat: float, lon: float) -> None:
        favorites = self.read()
        if any(f["city"] == city for f in favorites):
            return
        favorites.append({"city": city, "lat": lat, "lon": lon})
        self.write(favorites)

    def remove(self, city: str) -> None:
        favorites = [f for f in self.read() if f["city"] != city]
        self.write(favorites)

    def reorder(self, new_order: list[dict]) -> None:
        self.write(new_order)

    def list(self) -> list[dict]:
        return self.read()


class HistoryStore(JSONStore):
    def __init__(self, max_items: int = 10):
        super().__init__(config.HISTORY_FILE, default=[])
        self.max_items = max_items

    def add(self, city: str) -> None:
        history = [h for h in self.read() if h != city]
        history.insert(0, city)
        self.write(history[: self.max_items])

    def list(self) -> list[str]:
        return self.read()

    def clear(self) -> None:
        self.write([])


class SettingsStore(JSONStore):
    def __init__(self):
        default = {
            "theme": config.DEFAULT_THEME,
            "temp_unit": config.DEFAULT_TEMP_UNIT,
            "wind_unit": config.DEFAULT_WIND_UNIT,
            "pressure_unit": "hpa",
            "language": config.DEFAULT_LANGUAGE,
            "refresh_minutes": config.AUTO_REFRESH_MINUTES,
            "last_city": None,
        }
        super().__init__(config.SETTINGS_FILE, default=default)

    def get(self, key: str) -> Any:
        return self.read().get(key)

    def set(self, key: str, value: Any) -> None:
        data = self.read()
        data[key] = value
        self.write(data)


class LastWeatherCache(JSONStore):
    """Stores the last successful weather payload per city for offline mode."""

    def __init__(self):
        super().__init__(config.CACHE_DIR / "last_weather.json", default={})

    def save(self, city: str, payload: dict) -> None:
        data = self.read()
        data[city] = payload
        self.write(data)

    def load(self, city: str) -> dict | None:
        return self.read().get(city)
