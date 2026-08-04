# WeatherWise

A modern Windows/desktop weather app built with Python and `customtkinter`. Live current conditions, 24-hour and 7-day forecasts, air quality, embedded charts, an interactive map, favorites, and dark/light theming.

## Features

- Current weather by city search, zip, or IP-based auto-location
- 24-hour forecast strip and 7-day forecast list
- Humidity, wind, pressure, visibility, sunrise/sunset, AQI stat cards
- Temperature / rain chance / wind charts (matplotlib, embedded)
- Interactive map with city marker (tkintermapview)
- Favorites and recent-search sidebar, stored locally in JSON
- Dark mode, light mode, Celsius/Fahrenheit, km/h/mph, hPa/mmHg
- Auto-refresh every 10 minutes, manual refresh, offline last-known-data fallback
- Friendly error banner with retry for no-internet / invalid city / API failures

## Known scope limits (being upfront)

A few items from an "everything" wishlist aren't included, on purpose, rather than faked:

- **True animated radar** and **pollen data** aren't available on OpenWeatherMap's free tiers - the Map tab instead shows a static city marker map, and the tile-overlay hooks for precipitation/clouds/temp/wind layers are in `map.py` ready to enable.
- **UV Index, full 7-day (not 3-hour-aggregated) forecast, and severe weather alerts** need OpenWeatherMap's **One Call 3.0** API, which requires a separate free subscription toggle on your OpenWeatherMap account (still free up to 1,000 calls/day). The code (`weather_api.py: get_onecall`) is ready - wire it into `ui.py` once you've subscribed.
- **Custom icon/animation assets** (rain/snow/thunder animations, a branded app icon) need real image/font files, which can't be generated here. The `assets/` folders are ready for you to drop files into. Weather conditions currently render as clean text glyphs instead.

## Project structure

```
WeatherWise/
├── app.py            # entry point, config validation, logging
├── main.py            # thin launcher (python main.py)
├── config.py           # paths, API key loading, defaults
├── models.py            # Location / WeatherData dataclasses
├── weather_api.py        # OpenWeatherMap client (current, forecast, AQI, geocode)
├── location.py             # IP-based location detection (forecast + settings logic
│                            # live inside weather_api.py / cache.py, not separate files)
├── charts.py                # matplotlib chart builders
├── map.py                    # tkintermapview wrapper
├── theme.py                   # color palette + condition gradients
├── cache.py                    # JSON persistence (favorites, history, settings, offline cache)
├── utils.py                     # unit conversion, icon glyphs, AQI/moon/dew point helpers
├── ui.py                         # the full customtkinter interface
├── requirements.txt
├── .env.example
├── .gitignore
├── assets/
│   ├── icons/  fonts/  images/  animations/
└── data/
    ├── favorites.json  history.json  settings.json
    └── cache/
```

## Installation

```bash
cd WeatherWise
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

## Adding your API key

1. Get a free key at openweathermap.org/api.
2. Copy `.env.example` to `.env`.
3. Replace `your_api_key_here` with your real key:
   ```
   OPENWEATHER_API_KEY=your_real_key_here
   ```
4. `.env` is gitignored - it will never be committed.

## Running

```bash
python main.py
```

## Future improvements

- Wire in One Call 3.0 for true 7-day forecast, UV index, and severe weather alerts
- Precipitation/clouds/wind radar tile overlays on the map (hooks already in `map.py`)
- Drag-to-reorder favorites, autocomplete search dropdown
- Desktop push notifications for storm/heat/cold alerts
- Custom app icon and splash screen once brand assets exist

## License

MIT - do whatever you like with it.
