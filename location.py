"""
location.py

Detects the user's approximate location via IP address (desktop apps
don't have GPS hardware, so IP-based geolocation is the standard approach).
Falls back gracefully if detection fails or there's no internet.
"""

import logging

import requests

from models import Location

logger = logging.getLogger(__name__)


class LocationError(Exception):
    """Raised when location detection fails (permission/network/parsing)."""
    pass


def detect_location_by_ip(timeout: int = 5) -> Location:
    """
    Uses ip-api.com (free, no API key required, HTTP only) to resolve
    the user's approximate location from their public IP address.
    """
    try:
        response = requests.get("http://ip-api.com/json/", timeout=timeout)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success":
            raise LocationError("Location permission denied or IP lookup failed.")

        return Location(
            city=data.get("city", "Unknown"),
            country=data.get("countryCode", ""),
            latitude=data["lat"],
            longitude=data["lon"],
        )
    except requests.exceptions.ConnectionError as e:
        raise LocationError("No internet connection.") from e
    except requests.exceptions.RequestException as e:
        raise LocationError(f"Location lookup failed: {e}") from e
    except (KeyError, ValueError) as e:
        raise LocationError(f"Unexpected location response: {e}") from e
