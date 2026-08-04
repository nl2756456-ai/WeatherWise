"""
weather_api.py

Handles all communication with OpenWeatherMap:
- Current weather
- 5-day / 3-hour forecast (free tier)
- One Call 3.0 (daily forecast + UV + alerts - requires free OWM subscription)
- Air pollution / AQI
- Geocoding (city name -> lat/lon)
"""

import logging
from datetime import datetime
from typing import Any

import requests

import config
from models import Location, WeatherData

logger = logging.getLogger(__name__)


class WeatherAPIError(Exception):
    """Raised for any weather-API-related failure. UI code only needs to catch this one type."""
    pass


class WeatherAPI:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or config.OPENWEATHER_API_KEY
        if not self.api_key:
            raise WeatherAPIError("No API key configured. Add it to your .env file.")
        self.session = requests.Session()

    # ------------------------------------------------------------------
    # Internal request helper
    # ------------------------------------------------------------------
    def _get(self, url: str, params: dict) -> dict:
        params = {**params, "appid": self.api_key}
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            status = response.status_code
            if status == 401:
                raise WeatherAPIError("Invalid API key.") from e
            if status == 404:
                raise WeatherAPIError("Location not found.") from e
            if status == 403:
                raise WeatherAPIError(
                    "This endpoint needs a One Call API subscription "
                    "(free tier available at openweathermap.org)."
                ) from e
            raise WeatherAPIError(f"API request failed ({status}).") from e
        except requests.exceptions.ConnectionError as e:
            raise WeatherAPIError("No internet connection.") from e
        except requests.exceptions.Timeout as e:
            raise WeatherAPIError("Request timed out.") from e
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Network error: {e}") from e

    # ------------------------------------------------------------------
    # Geocoding
    # ------------------------------------------------------------------
    def geocode(self, city: str) -> Location:
        """Resolve a free-text city/zip/country query into a Location."""
        url = f"{config.OPENWEATHER_GEO_URL}/direct"
        data = self._get(url, {"q": city, "limit": 1})
        if not data:
            raise WeatherAPIError(f"City not found: {city}")
        entry = data[0]
        return Location(
            city=entry["name"],
            country=entry.get("country", ""),
            latitude=entry["lat"],
            longitude=entry["lon"],
        )

    def reverse_geocode(self, lat: float, lon: float) -> Location:
        url = f"{config.OPENWEATHER_GEO_URL}/reverse"
        data = self._get(url, {"lat": lat, "lon": lon, "limit": 1})
        if not data:
            return Location(city="Unknown", country="", latitude=lat, longitude=lon)
        entry = data[0]
        return Location(
            city=entry["name"],
            country=entry.get("country", ""),
            latitude=lat,
            longitude=lon,
        )

    # ------------------------------------------------------------------
    # Current weather
    # ------------------------------------------------------------------
    def get_current_weather(
        self,
        city: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
        units: str = "metric",
    ) -> WeatherData:
        params: dict[str, Any] = {"units": units}
        if city:
            params["q"] = city
        elif lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        else:
            raise ValueError("Provide either a city name or lat/lon coordinates.")

        url = f"{config.OPENWEATHER_BASE_URL}/weather"
        data = self._get(url, params)
        return self._parse_current(data)

    def _parse_current(self, data: dict) -> WeatherData:
        try:
            location = Location(
                city=data["name"],
                country=data["sys"]["country"],
                latitude=data["coord"]["lat"],
                longitude=data["coord"]["lon"],
                timezone_offset=data.get("timezone", 0),
            )
            return WeatherData(
                location=location,
                temperature=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                temp_min=data["main"]["temp_min"],
                temp_max=data["main"]["temp_max"],
                humidity=data["main"]["humidity"],
                pressure=data["main"]["pressure"],
                wind_speed=data["wind"]["speed"],
                wind_direction=data["wind"].get("deg", 0),
                visibility=data.get("visibility", 0),
                cloud_percent=data["clouds"]["all"],
                description=data["weather"][0]["description"],
                icon_code=data["weather"][0]["icon"],
                sunrise=datetime.fromtimestamp(data["sys"]["sunrise"]),
                sunset=datetime.fromtimestamp(data["sys"]["sunset"]),
            )
        except (KeyError, IndexError) as e:
            raise WeatherAPIError(f"Unexpected API response format: {e}") from e

    # ------------------------------------------------------------------
    # 5-day / 3-hour forecast (free tier) - used for hourly strip
    # ------------------------------------------------------------------
    def get_hourly_forecast(self, lat: float, lon: float, units: str = "metric") -> list[dict]:
        url = f"{config.OPENWEATHER_BASE_URL}/forecast"
        data = self._get(url, {"lat": lat, "lon": lon, "units": units})
        entries = []
        for item in data.get("list", [])[:8]:  # next 24h in 3h steps
            entries.append({
                "time": datetime.fromtimestamp(item["dt"]),
                "temp": item["main"]["temp"],
                "icon": item["weather"][0]["icon"],
                "description": item["weather"][0]["description"],
                "pop": item.get("pop", 0.0) * 100,  # probability of precipitation
                "wind_speed": item["wind"]["speed"],
            })
        return entries

    def get_daily_forecast_from_3h(self, lat: float, lon: float, units: str = "metric") -> list[dict]:
        """
        Build a rough daily forecast by aggregating the 5-day/3-hour data.
        Free-tier fallback when One Call isn't available. Gives up to 5 days.
        """
        url = f"{config.OPENWEATHER_BASE_URL}/forecast"
        data = self._get(url, {"lat": lat, "lon": lon, "units": units})

        by_day: dict[str, list[dict]] = {}
        for item in data.get("list", []):
            dt = datetime.fromtimestamp(item["dt"])
            key = dt.strftime("%Y-%m-%d")
            by_day.setdefault(key, []).append(item)

        daily = []
        for day_key, items in list(by_day.items())[:7]:
            temps = [i["main"]["temp"] for i in items]
            pops = [i.get("pop", 0.0) for i in items]
            midday = min(items, key=lambda i: abs(datetime.fromtimestamp(i["dt"]).hour - 13))
            daily.append({
                "date": datetime.strptime(day_key, "%Y-%m-%d"),
                "temp_min": min(temps),
                "temp_max": max(temps),
                "icon": midday["weather"][0]["icon"],
                "description": midday["weather"][0]["description"],
                "pop": max(pops) * 100,
            })
        return daily

    # ------------------------------------------------------------------
    # One Call 3.0 - richer daily forecast, UV index, alerts
    # (requires a free subscription toggle on openweathermap.org)
    # ------------------------------------------------------------------
    def get_onecall(self, lat: float, lon: float, units: str = "metric") -> dict:
        url = "https://api.openweathermap.org/data/3.0/onecall"
        data = self._get(url, {
            "lat": lat, "lon": lon, "units": units,
            "exclude": "minutely",
        })
        return data

    # ------------------------------------------------------------------
    # Air quality
    # ------------------------------------------------------------------
    def get_air_quality(self, lat: float, lon: float) -> dict:
        url = "https://api.openweathermap.org/data/2.5/air_pollution"
        data = self._get(url, {"lat": lat, "lon": lon})
        try:
            entry = data["list"][0]
            return {
                "aqi": entry["main"]["aqi"],
                "components": entry["components"],
            }
        except (KeyError, IndexError) as e:
            raise WeatherAPIError(f"Unexpected air quality response: {e}") from e
