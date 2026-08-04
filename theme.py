"""
theme.py

Color palette, gradients-per-weather-condition, and dark/light mode
definitions used across the UI.
"""

PRIMARY = "#4F8EF7"
ACCENT = "#00C2FF"

DARK = {
    "bg": "#0B1220",
    "surface": "#141C2F",
    "surface_alt": "#1B2540",
    "text_primary": "#F5F7FA",
    "text_secondary": "#9AA5B8",
    "border": "#243252",
    "primary": PRIMARY,
    "accent": ACCENT,
    "danger": "#FF5C5C",
    "warning": "#FFB84C",
}

LIGHT = {
    "bg": "#EAF2FF",
    "surface": "#FFFFFF",
    "surface_alt": "#F2F6FF",
    "text_primary": "#101828",
    "text_secondary": "#5B6472",
    "border": "#D7E1F2",
    "primary": PRIMARY,
    "accent": ACCENT,
    "danger": "#D92D20",
    "warning": "#B54708",
}

# Background gradient (start, end) chosen per weather condition group.
# Used to color the hero section / window background dynamically.
CONDITION_GRADIENTS = {
    "clear_day":    ("#4F8EF7", "#00C2FF"),
    "clear_night":  ("#0B1220", "#1B2540"),
    "clouds":       ("#5B6C8F", "#8CA0C4"),
    "rain":         ("#33475B", "#4F6B8A"),
    "thunderstorm": ("#1E2438", "#3B3F63"),
    "snow":         ("#8FA8C9", "#DCE8F7"),
    "mist":         ("#7C8798", "#A9B4C4"),
}


def gradient_for(icon_code: str) -> tuple[str, str]:
    """Map an OpenWeatherMap icon code to a background gradient key."""
    is_night = icon_code.endswith("n")
    prefix = icon_code[:2]
    mapping = {
        "01": "clear_night" if is_night else "clear_day",
        "02": "clouds", "03": "clouds", "04": "clouds",
        "09": "rain", "10": "rain",
        "11": "thunderstorm",
        "13": "snow",
        "50": "mist",
    }
    key = mapping.get(prefix, "clouds")
    return CONDITION_GRADIENTS[key]


def palette(mode: str = "dark") -> dict:
    return DARK if mode == "dark" else LIGHT
