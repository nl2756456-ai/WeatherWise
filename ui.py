"""
ui.py

The full WeatherWise interface, built with customtkinter for a modern,
rounded, glass-like look. Handles layout, theming, and wiring user
actions to the backend modules. All network calls run on background
threads and post results back to the Tk main thread via `after()`.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import charts
import theme
import utils
from cache import FavoritesStore, HistoryStore, LastWeatherCache, SettingsStore
from location import LocationError, detect_location_by_ip
from models import WeatherData
from weather_api import WeatherAPI, WeatherAPIError

logger = logging.getLogger(__name__)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class StatCard(ctk.CTkFrame):
    """Small metric card: icon-ish label + value, used in the stats grid."""

    def __init__(self, parent, title: str, value: str = "--", **kwargs):
        super().__init__(parent, corner_radius=14, fg_color=("#F2F6FF", "#1B2540"), **kwargs)
        self.title_label = ctk.CTkLabel(self, text=title, font=("", 12), text_color=("#5B6472", "#9AA5B8"))
        self.title_label.pack(anchor="w", padx=14, pady=(12, 0))
        self.value_label = ctk.CTkLabel(self, text=value, font=("", 20, "bold"))
        self.value_label.pack(anchor="w", padx=14, pady=(0, 12))

    def set_value(self, value: str) -> None:
        self.value_label.configure(text=value)


class HourCard(ctk.CTkFrame):
    def __init__(self, parent, time_label: str, icon: str, temp: str, pop: str, **kwargs):
        super().__init__(parent, corner_radius=14, fg_color=("#F2F6FF", "#1B2540"), width=76)
        ctk.CTkLabel(self, text=time_label, font=("", 11), text_color=("#5B6472", "#9AA5B8")).pack(pady=(10, 2))
        ctk.CTkLabel(self, text=icon, font=("", 22)).pack(pady=2)
        ctk.CTkLabel(self, text=temp, font=("", 14, "bold")).pack(pady=2)
        ctk.CTkLabel(self, text=pop, font=("", 10), text_color="#00C2FF").pack(pady=(0, 10))


class DayRow(ctk.CTkFrame):
    def __init__(self, parent, day_label: str, icon: str, lo: str, hi: str, pop: str, **kwargs):
        super().__init__(parent, corner_radius=12, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self, text=day_label, font=("", 13), width=90, anchor="w").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ctk.CTkLabel(self, text=icon, font=("", 16)).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(self, text=pop, font=("", 11), text_color="#00C2FF", width=50).grid(row=0, column=2)
        ctk.CTkLabel(self, text=lo, font=("", 13), text_color=("#5B6472", "#9AA5B8"), width=40).grid(row=0, column=3)
        ctk.CTkLabel(self, text=hi, font=("", 13, "bold"), width=40).grid(row=0, column=4, padx=(0, 8))


class WeatherWiseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WeatherWise")
        self.geometry("1000x680")
        self.minsize(860, 600)

        self.api = WeatherAPI()
        self.favorites = FavoritesStore()
        self.history = HistoryStore()
        self.settings = SettingsStore()
        self.last_weather_cache = LastWeatherCache()

        self.temp_unit = self.settings.get("temp_unit") or "metric"
        self.wind_unit = self.settings.get("wind_unit") or "kmh"
        self.pressure_unit = self.settings.get("pressure_unit") or "hpa"
        appearance = self.settings.get("theme") or "dark"
        ctk.set_appearance_mode(appearance)

        self.current_weather: WeatherData | None = None
        self._refresh_job = None

        self._build_layout()
        self._start_initial_load()
        self._schedule_auto_refresh()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        self._build_topbar(main)

        self.tabs = ctk.CTkTabview(main, corner_radius=16)
        self.tabs.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        self.tabs.add("Today")
        self.tabs.add("Forecast")
        self.tabs.add("Charts")
        self.tabs.add("Map")
        self.tabs.add("Settings")

        self._build_today_tab(self.tabs.tab("Today"))
        self._build_forecast_tab(self.tabs.tab("Forecast"))
        self._build_charts_tab(self.tabs.tab("Charts"))
        self._build_map_tab(self.tabs.tab("Map"))
        self._build_settings_tab(self.tabs.tab("Settings"))

        self.status_bar = ctk.CTkLabel(self, text="", font=("", 11), text_color=("#5B6472", "#9AA5B8"))
        self.status_bar.grid(row=1, column=1, sticky="w", padx=24, pady=(0, 6))

    def _build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("#EAF2FF", "#0B1220"))
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="WeatherWise", font=("", 18, "bold")).pack(padx=18, pady=(20, 10), anchor="w")

        ctk.CTkLabel(sidebar, text="FAVORITES", font=("", 11, "bold"), text_color=("#5B6472", "#9AA5B8")).pack(padx=18, pady=(10, 4), anchor="w")
        self.favorites_list_frame = ctk.CTkScrollableFrame(sidebar, fg_color="transparent", height=180)
        self.favorites_list_frame.pack(fill="x", padx=10)

        ctk.CTkLabel(sidebar, text="RECENT", font=("", 11, "bold"), text_color=("#5B6472", "#9AA5B8")).pack(padx=18, pady=(16, 4), anchor="w")
        self.recent_list_frame = ctk.CTkScrollableFrame(sidebar, fg_color="transparent", height=160)
        self.recent_list_frame.pack(fill="x", padx=10)

        ctk.CTkButton(sidebar, text="Use my location", command=self._use_current_location).pack(
            side="bottom", padx=18, pady=18, fill="x"
        )

        self._refresh_sidebar_lists()

    def _build_topbar(self, parent) -> None:
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(1, weight=1)

        self.city_label = ctk.CTkLabel(top, text="Loading...", font=("", 20, "bold"))
        self.city_label.grid(row=0, column=0, sticky="w")

        self.search_entry = ctk.CTkEntry(top, placeholder_text="Search city, zip, or coordinates", width=280)
        self.search_entry.grid(row=0, column=1, sticky="e", padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self._on_search())

        ctk.CTkButton(top, text="Search", width=80, command=self._on_search).grid(row=0, column=2, padx=(0, 8))
        self.refresh_btn = ctk.CTkButton(top, text="Refresh", width=80, command=self._refresh_weather)
        self.refresh_btn.grid(row=0, column=3)

    def _build_today_tab(self, tab) -> None:
        tab.grid_columnconfigure(0, weight=1)

        self.error_banner = ctk.CTkFrame(tab, fg_color="#D92D20", corner_radius=12)
        self.error_label = ctk.CTkLabel(self.error_banner, text="", text_color="white", font=("", 12))
        self.error_label.pack(side="left", padx=14, pady=10)
        ctk.CTkButton(self.error_banner, text="Retry", width=70, fg_color="white", text_color="#D92D20",
                      command=self._refresh_weather).pack(side="right", padx=10, pady=8)

        hero = ctk.CTkFrame(tab, corner_radius=20, fg_color=("#4F8EF7", "#141C2F"))
        hero.grid(row=1, column=0, sticky="ew", pady=(4, 16))
        hero.grid_columnconfigure(0, weight=1)

        self.icon_label = ctk.CTkLabel(hero, text="?", font=("", 64))
        self.icon_label.pack(pady=(20, 0))
        self.temp_label = ctk.CTkLabel(hero, text="--°", font=("", 52, "bold"), text_color="white")
        self.temp_label.pack()
        self.desc_label = ctk.CTkLabel(hero, text="", font=("", 15), text_color="white")
        self.desc_label.pack(pady=(0, 6))
        self.feels_label = ctk.CTkLabel(hero, text="", font=("", 12), text_color="#EAF2FF")
        self.feels_label.pack(pady=(0, 20))

        grid = ctk.CTkFrame(tab, fg_color="transparent")
        grid.grid(row=2, column=0, sticky="ew")
        for i in range(4):
            grid.grid_columnconfigure(i, weight=1, uniform="stat")

        self.stat_cards = {}
        stat_names = [
            "Humidity", "Wind", "Pressure", "Visibility",
            "UV Index", "Sunrise", "Sunset", "AQI",
        ]
        for idx, name in enumerate(stat_names):
            card = StatCard(grid, name)
            card.grid(row=idx // 4, column=idx % 4, padx=6, pady=6, sticky="ew")
            self.stat_cards[name] = card

        ctk.CTkLabel(tab, text="Next 24 hours", font=("", 13, "bold")).grid(row=3, column=0, sticky="w", pady=(16, 4))
        self.hourly_frame = ctk.CTkScrollableFrame(tab, orientation="horizontal", height=110, fg_color="transparent")
        self.hourly_frame.grid(row=4, column=0, sticky="ew")

    def _build_forecast_tab(self, tab) -> None:
        tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(tab, text="7-day forecast", font=("", 14, "bold")).pack(anchor="w", padx=8, pady=(8, 4))
        self.daily_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.daily_frame.pack(fill="both", expand=True, padx=4)

    def _build_charts_tab(self, tab) -> None:
        self.charts_container = ctk.CTkFrame(tab, fg_color="transparent")
        self.charts_container.pack(fill="both", expand=True, padx=8, pady=8)
        ctk.CTkLabel(self.charts_container, text="Charts will appear after weather loads.",
                     text_color=("#5B6472", "#9AA5B8")).pack(pady=40)

    def _build_map_tab(self, tab) -> None:
        self.map_tab = tab
        self._map_widget = None  # lazily created (needs a real city first)
        ctk.CTkLabel(tab, text="Map will appear after weather loads.",
                     text_color=("#5B6472", "#9AA5B8")).pack(pady=40)

    def _build_settings_tab(self, tab) -> None:
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tab, text="Appearance", font=("", 13, "bold")).grid(row=0, column=0, sticky="w", pady=(8, 4))
        self.theme_menu = ctk.CTkOptionMenu(tab, values=["dark", "light", "system"], command=self._on_theme_change)
        self.theme_menu.set(self.settings.get("theme") or "dark")
        self.theme_menu.grid(row=1, column=0, sticky="w", pady=(0, 16))

        ctk.CTkLabel(tab, text="Temperature unit", font=("", 13, "bold")).grid(row=2, column=0, sticky="w", pady=(8, 4))
        self.temp_unit_menu = ctk.CTkOptionMenu(tab, values=["Celsius (°C)", "Fahrenheit (°F)"], command=self._on_temp_unit_change)
        self.temp_unit_menu.set("Celsius (°C)" if self.temp_unit == "metric" else "Fahrenheit (°F)")
        self.temp_unit_menu.grid(row=3, column=0, sticky="w", pady=(0, 16))

        ctk.CTkLabel(tab, text="Wind unit", font=("", 13, "bold")).grid(row=4, column=0, sticky="w", pady=(8, 4))
        self.wind_unit_menu = ctk.CTkOptionMenu(tab, values=["km/h", "mph"], command=self._on_wind_unit_change)
        self.wind_unit_menu.set("km/h" if self.wind_unit == "kmh" else "mph")
        self.wind_unit_menu.grid(row=5, column=0, sticky="w", pady=(0, 16))

        ctk.CTkLabel(tab, text="Pressure unit", font=("", 13, "bold")).grid(row=6, column=0, sticky="w", pady=(8, 4))
        self.pressure_unit_menu = ctk.CTkOptionMenu(tab, values=["hPa", "mmHg"], command=self._on_pressure_unit_change)
        self.pressure_unit_menu.set("hPa" if self.pressure_unit == "hpa" else "mmHg")
        self.pressure_unit_menu.grid(row=7, column=0, sticky="w", pady=(0, 16))

    # ------------------------------------------------------------------
    # Sidebar list rendering
    # ------------------------------------------------------------------
    def _refresh_sidebar_lists(self) -> None:
        for widget in self.favorites_list_frame.winfo_children():
            widget.destroy()
        for fav in self.favorites.list():
            row = ctk.CTkFrame(self.favorites_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkButton(row, text=fav["city"], anchor="w", fg_color="transparent",
                          command=lambda f=fav: self._load_weather(lat=f["lat"], lon=f["lon"], label=f["city"])
                          ).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(row, text="x", width=26, fg_color="transparent",
                          command=lambda f=fav: self._remove_favorite(f["city"])).pack(side="right")

        for widget in self.recent_list_frame.winfo_children():
            widget.destroy()
        for city in self.history.list():
            ctk.CTkButton(self.recent_list_frame, text=city, anchor="w", fg_color="transparent",
                          command=lambda c=city: self._search_city(c)).pack(fill="x", pady=2)

    def _remove_favorite(self, city: str) -> None:
        self.favorites.remove(city)
        self._refresh_sidebar_lists()

    # ------------------------------------------------------------------
    # Data loading (threaded)
    # ------------------------------------------------------------------
    def _start_initial_load(self) -> None:
        last_city = self.settings.get("last_city")
        if last_city:
            self._search_city(last_city)
        else:
            self._use_current_location()

    def _use_current_location(self) -> None:
        self._set_loading()

        def worker():
            try:
                loc = detect_location_by_ip()
                self.after(0, lambda: self._load_weather(lat=loc.latitude, lon=loc.longitude, label=loc.city))
            except LocationError as e:
                self.after(0, lambda: self._show_error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_search(self) -> None:
        query = self.search_entry.get().strip()
        if query:
            self._search_city(query)

    def _search_city(self, query: str) -> None:
        self._set_loading()

        def worker():
            try:
                loc = self.api.geocode(query)
                self.after(0, lambda: self._load_weather(lat=loc.latitude, lon=loc.longitude, label=loc.city))
            except WeatherAPIError as e:
                self.after(0, lambda: self._show_error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _load_weather(self, lat: float, lon: float, label: str) -> None:
        self._set_loading()

        def worker():
            try:
                weather = self.api.get_current_weather(lat=lat, lon=lon, units=self.temp_unit)
                hourly = self.api.get_hourly_forecast(lat, lon, units=self.temp_unit)
                daily = self.api.get_daily_forecast_from_3h(lat, lon, units=self.temp_unit)
                try:
                    aqi = self.api.get_air_quality(lat, lon)
                except WeatherAPIError:
                    aqi = None

                self.history.add(weather.location.city)
                self.settings.set("last_city", weather.location.city)
                self.last_weather_cache.save(weather.location.city, {
                    "temp": weather.temperature, "description": weather.description,
                })

                self.after(0, lambda: self._render_weather(weather, hourly, daily, aqi))
            except WeatherAPIError as e:
                cached = self.last_weather_cache.load(label)
                if cached:
                    self.after(0, lambda: self._show_error(f"{e} Showing last known data."))
                else:
                    self.after(0, lambda: self._show_error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _refresh_weather(self) -> None:
        if self.current_weather:
            loc = self.current_weather.location
            self._load_weather(loc.latitude, loc.longitude, loc.city)
        else:
            self._start_initial_load()

    def _schedule_auto_refresh(self) -> None:
        interval_ms = (self.settings.get("refresh_minutes") or 10) * 60 * 1000
        self._refresh_job = self.after(interval_ms, self._auto_refresh_tick)

    def _auto_refresh_tick(self) -> None:
        self._refresh_weather()
        self._schedule_auto_refresh()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def _set_loading(self) -> None:
        self.error_banner.grid_forget()
        self.city_label.configure(text="Loading...")
        self.status_bar.configure(text="Fetching latest weather...")

    def _show_error(self, message: str) -> None:
        self.error_label.configure(text=message)
        self.error_banner.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.status_bar.configure(text="")

    def _render_weather(self, weather: WeatherData, hourly: list[dict], daily: list[dict], aqi: dict | None) -> None:
        self.current_weather = weather
        self.error_banner.grid_forget()

        self.city_label.configure(text=f"{weather.location.city}, {weather.location.country}")
        self.icon_label.configure(text=utils.icon_symbol(weather.icon_code))
        self.temp_label.configure(text=utils.format_temp(weather.temperature, self.temp_unit))
        self.desc_label.configure(text=weather.description.title())
        self.feels_label.configure(text=f"Feels like {utils.format_temp(weather.feels_like, self.temp_unit)}")

        self.stat_cards["Humidity"].set_value(f"{weather.humidity}%")
        self.stat_cards["Wind"].set_value(
            f"{utils.format_wind(weather.wind_speed, self.wind_unit)} {utils.degrees_to_compass(weather.wind_direction)}"
        )
        self.stat_cards["Pressure"].set_value(utils.format_pressure(weather.pressure, self.pressure_unit))
        self.stat_cards["Visibility"].set_value(utils.format_visibility_km(weather.visibility))
        self.stat_cards["UV Index"].set_value("N/A")
        self.stat_cards["Sunrise"].set_value(utils.format_time(weather.sunrise))
        self.stat_cards["Sunset"].set_value(utils.format_time(weather.sunset))
        if aqi:
            label, _ = utils.aqi_label(aqi["aqi"])
            self.stat_cards["AQI"].set_value(f"{aqi['aqi']} · {label}")
        else:
            self.stat_cards["AQI"].set_value("N/A")

        for widget in self.hourly_frame.winfo_children():
            widget.destroy()
        for h in hourly:
            card = HourCard(
                self.hourly_frame,
                time_label=h["time"].strftime("%H:%M"),
                icon=utils.icon_symbol(h["icon"]),
                temp=utils.format_temp(h["temp"], self.temp_unit),
                pop=f"{round(h['pop'])}%",
            )
            card.pack(side="left", padx=4, pady=6)

        for widget in self.daily_frame.winfo_children():
            widget.destroy()
        for d in daily:
            row = DayRow(
                self.daily_frame,
                day_label=d["date"].strftime("%A"),
                icon=utils.icon_symbol(d["icon"]),
                lo=utils.format_temp(d["temp_min"], self.temp_unit),
                hi=utils.format_temp(d["temp_max"], self.temp_unit),
                pop=f"{round(d['pop'])}%",
            )
            row.pack(fill="x", pady=2)

        self._render_charts(hourly)
        self._render_map(weather)

        self.status_bar.configure(text=f"Updated {datetime.now().strftime('%H:%M:%S')}")

    def _render_charts(self, hourly: list[dict]) -> None:
        for widget in self.charts_container.winfo_children():
            widget.destroy()

        mode = ctk.get_appearance_mode().lower()
        pal = theme.palette(mode)

        for builder, title in [
            (charts.temperature_chart, "Temperature"),
            (charts.rain_chance_chart, "Chance of rain"),
            (charts.wind_chart, "Wind speed"),
        ]:
            ctk.CTkLabel(self.charts_container, text=title, font=("", 12, "bold")).pack(anchor="w", pady=(8, 0))
            fig = builder(hourly, fg=pal["text_primary"], bg=pal["surface"], accent=pal["primary"])
            canvas = FigureCanvasTkAgg(fig, master=self.charts_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="x", pady=(4, 8))

    def _render_map(self, weather: WeatherData) -> None:
        try:
            import map as map_module
        except ImportError:
            return

        for widget in self.map_tab.winfo_children():
            widget.destroy()

        weather_map = map_module.WeatherMap(self.map_tab, width=700, height=380)
        weather_map.pack(fill="both", expand=True, padx=8, pady=8)
        weather_map.show_city(weather.location.latitude, weather.location.longitude, weather.location.city)
        self._map_widget = weather_map

    # ------------------------------------------------------------------
    # Settings handlers
    # ------------------------------------------------------------------
    def _on_theme_change(self, value: str) -> None:
        ctk.set_appearance_mode(value)
        self.settings.set("theme", value)
        if self.current_weather:
            self._render_charts(self._last_hourly_cache if hasattr(self, "_last_hourly_cache") else [])

    def _on_temp_unit_change(self, value: str) -> None:
        self.temp_unit = "metric" if "Celsius" in value else "imperial"
        self.settings.set("temp_unit", self.temp_unit)
        self._refresh_weather()

    def _on_wind_unit_change(self, value: str) -> None:
        self.wind_unit = "kmh" if value == "km/h" else "mph"
        self.settings.set("wind_unit", self.wind_unit)
        if self.current_weather:
            self._refresh_weather()

    def _on_pressure_unit_change(self, value: str) -> None:
        self.pressure_unit = "hpa" if value == "hPa" else "mmhg"
        self.settings.set("pressure_unit", self.pressure_unit)
        if self.current_weather:
            self._refresh_weather()
