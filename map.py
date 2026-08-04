"""
map.py

Wraps tkintermapview to show the searched city and the user's detected
location, with zoom controls and markers. Also supports adding an
OpenWeatherMap precipitation/clouds/temp tile overlay.
"""

import tkintermapview

import config


TILE_LAYERS = {
    "precipitation": f"https://tile.openweathermap.org/map/precipitation_new/{{z}}/{{x}}/{{y}}.png?appid={config.OPENWEATHER_API_KEY}",
    "clouds": f"https://tile.openweathermap.org/map/clouds_new/{{z}}/{{x}}/{{y}}.png?appid={config.OPENWEATHER_API_KEY}",
    "temp": f"https://tile.openweathermap.org/map/temp_new/{{z}}/{{x}}/{{y}}.png?appid={config.OPENWEATHER_API_KEY}",
    "wind": f"https://tile.openweathermap.org/map/wind_new/{{z}}/{{x}}/{{y}}.png?appid={config.OPENWEATHER_API_KEY}",
}


class WeatherMap:
    """Encapsulates a tkintermapview widget with weather overlay support."""

    def __init__(self, parent, width: int = 600, height: int = 350):
        self.widget = tkintermapview.TkinterMapView(parent, width=width, height=height, corner_radius=12)
        self._city_marker = None
        self._user_marker = None
        self._overlay_path = None

    def show_city(self, lat: float, lon: float, label: str) -> None:
        self.widget.set_position(lat, lon)
        self.widget.set_zoom(10)
        if self._city_marker:
            self._city_marker.delete()
        self._city_marker = self.widget.set_marker(lat, lon, text=label)

    def show_user_location(self, lat: float, lon: float) -> None:
        if self._user_marker:
            self._user_marker.delete()
        self._user_marker = self.widget.set_marker(lat, lon, text="You", marker_color_circle="#00C2FF")

    def set_overlay(self, layer: str | None) -> None:
        """layer in {'precipitation', 'clouds', 'temp', 'wind', None}"""
        if self._overlay_path:
            self.widget.delete_path(self._overlay_path) if hasattr(self.widget, "delete_path") else None
            self._overlay_path = None
        if layer and layer in TILE_LAYERS:
            self.widget.set_overlay_tile_server(TILE_LAYERS[layer])
        else:
            self.widget.set_overlay_tile_server(None)

    def set_zoom(self, level: int) -> None:
        self.widget.set_zoom(level)

    def grid(self, **kwargs) -> None:
        self.widget.grid(**kwargs)

    def pack(self, **kwargs) -> None:
        self.widget.pack(**kwargs)
