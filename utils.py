"""
utils.py

Small reusable helpers: unit conversion, icon symbols, formatting,
AQI categorization, wind direction, moon phase calculation.
"""

import math
from datetime import datetime, date


# ---------------------------------------------------------------------------
# Unit conversion
# ---------------------------------------------------------------------------

def celsius_to_fahrenheit(c: float) -> float:
    return (c * 9 / 5) + 32


def kmh_to_mph(kmh: float) -> float:
    return kmh * 0.621371


def hpa_to_mmhg(hpa: float) -> float:
    return hpa * 0.750062


def format_temp(value_c: float, unit: str = "metric") -> str:
    if unit == "imperial":
        return f"{round(celsius_to_fahrenheit(value_c))}°F"
    return f"{round(value_c)}°C"


def format_wind(speed_ms: float, unit: str = "kmh") -> str:
    kmh = speed_ms * 3.6
    if unit == "mph":
        return f"{round(kmh_to_mph(kmh))} mph"
    return f"{round(kmh)} km/h"


def format_pressure(hpa: float, unit: str = "hpa") -> str:
    if unit == "mmhg":
        return f"{round(hpa_to_mmhg(hpa))} mmHg"
    return f"{round(hpa)} hPa"


# ---------------------------------------------------------------------------
# Wind direction compass
# ---------------------------------------------------------------------------

_COMPASS_POINTS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
]


def degrees_to_compass(deg: float) -> str:
    idx = round(deg / 22.5) % 16
    return _COMPASS_POINTS[idx]


# ---------------------------------------------------------------------------
# Weather icon symbols (unicode glyphs - no external image files needed)
# ---------------------------------------------------------------------------

_ICON_MAP = {
    "01d": "☀",  "01n": "☾",
    "02d": "⛅", "02n": "☁",
    "03d": "☁",  "03n": "☁",
    "04d": "☁",  "04n": "☁",
    "09d": "🌧", "09n": "🌧",
    "10d": "🌦", "10n": "🌧",
    "11d": "⛈",  "11n": "⛈",
    "13d": "❄",  "13n": "❄",
    "50d": "🌫", "50n": "🌫",
}


def icon_symbol(icon_code: str) -> str:
    return _ICON_MAP.get(icon_code, "?")


# ---------------------------------------------------------------------------
# Air Quality Index categorization (OpenWeatherMap AQI scale: 1-5)
# ---------------------------------------------------------------------------

_AQI_LABELS = {
    1: ("Good", "Air quality is satisfactory."),
    2: ("Fair", "Air quality is acceptable."),
    3: ("Moderate", "Sensitive groups should reduce prolonged outdoor exertion."),
    4: ("Poor", "Everyone may begin to experience health effects."),
    5: ("Very poor", "Health warnings of emergency conditions."),
}


def aqi_label(aqi: int) -> tuple[str, str]:
    return _AQI_LABELS.get(aqi, ("Unknown", ""))


# ---------------------------------------------------------------------------
# Moon phase (pure calculation, no API needed)
# ---------------------------------------------------------------------------

_MOON_PHASE_NAMES = [
    "New moon", "Waxing crescent", "First quarter", "Waxing gibbous",
    "Full moon", "Waning gibbous", "Last quarter", "Waning crescent",
]


def moon_phase(for_date: date | None = None) -> str:
    """
    Approximate moon phase name using a fixed synodic month length.
    Reference new moon: 2000-01-06.
    """
    for_date = for_date or date.today()
    reference = date(2000, 1, 6)
    days_since = (for_date - reference).days
    synodic_month = 29.53058867
    position = (days_since % synodic_month) / synodic_month
    index = round(position * 8) % 8
    return _MOON_PHASE_NAMES[index]


# ---------------------------------------------------------------------------
# Dew point (Magnus formula approximation)
# ---------------------------------------------------------------------------

def dew_point(temp_c: float, humidity_pct: float) -> float:
    a, b = 17.27, 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity_pct / 100.0)
    return (b * alpha) / (a - alpha)


# ---------------------------------------------------------------------------
# Misc formatting
# ---------------------------------------------------------------------------

def format_time(dt: datetime) -> str:
    return dt.strftime("%I:%M %p").lstrip("0")


def format_visibility_km(meters: int) -> str:
    return f"{meters / 1000:.1f} km"
