from flask import Flask, render_template, request
from weather_api import WeatherAPI, WeatherAPIError

app = Flask(__name__)
weather_api = WeatherAPI()


def get_weather_page(weather=None, error=None):
    forecast = None
    hourly = None
    aqi = None

    if weather:
        lat = weather.location.latitude
        lon = weather.location.longitude
        forecast = weather_api.get_daily_forecast_from_3h(lat, lon)
        hourly = weather_api.get_hourly_forecast(lat, lon)
        aqi = weather_api.get_air_quality(lat, lon)

    return render_template(
        "index.html",
        weather=weather,
        forecast=forecast,
        hourly=hourly,
        aqi=aqi,
        error=error,
    )


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        city = request.form.get("city", "").strip()

        if not city:
            return get_weather_page(error="Please enter a city name.")

        try:
            weather = weather_api.get_current_weather(city=city)
            return get_weather_page(weather=weather)
        except WeatherAPIError as e:
            return get_weather_page(error=str(e))

    return get_weather_page()


@app.route("/location")
def location():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    try:
        if lat is None or lon is None:
            return get_weather_page(error="Location coordinates are missing.")

        weather = weather_api.get_current_weather(
            lat=float(lat),
            lon=float(lon),
        )
        return get_weather_page(weather=weather)

    except (ValueError, TypeError):
        return get_weather_page(error="Invalid location coordinates.")
    except WeatherAPIError as e:
        return get_weather_page(error=str(e))


if __name__ == "__main__":
    app.run(debug=True)
