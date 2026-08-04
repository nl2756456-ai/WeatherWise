"""
models.py

Defines the data structures WeatherWise uses to represent weather
information. Keeping this separate means every other file (weather_api.py,
app.py, charts.py...) works with the SAME predictable object shape,
instead of raw, error-prone JSON dictionaries.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Location:
    """Represents a geographic location the user searched for."""
    city: str
    country: str
    latitude: float
    longitude: float
    timezone_offset: int = 0  # seconds offset from UTC

    def coordinates(self) -> tuple[float, float]:
        """Return (lat, lon) as a tuple - useful for the map widget."""
        return (self.latitude, self.longitude)


@dataclass
class WeatherData:
    """
    Represents a single weather snapshot for a location.
    This is the object every part of the app will pass around
    instead of raw API JSON.
    """
    location: Location
    temperature: float
    feels_like: float
    temp_min: float
    temp_max: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_direction: int
    visibility: int
    cloud_percent: int
    description: str
    icon_code: str
    sunrise: datetime
    sunset: datetime
    fetched_at: datetime = field(default_factory=datetime.now)

    def is_stale(self, max_age_minutes: int = 10) -> bool:
        """
        Check whether this weather snapshot is too old to trust.
        Used later by cache.py to decide whether to show cached data
        or fetch fresh data.
        """
        age_seconds = (datetime.now() - self.fetched_at).total_seconds()
        return age_seconds > (max_age_minutes * 60)
