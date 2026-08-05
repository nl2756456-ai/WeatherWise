from flask import Flask, render_template, request
from weather_api import WeatherAPI, WeatherAPIError

app = Flask(__name__)
weather_api = WeatherAPI()


@app.route("/", methods=["GET", "POST"])
def home():
    aqi = None

    weather = None
    forecast = None
    error = None

    if request.method == "POST":
        city = request.form["city"]

        try:
            weather = weather_api.get_current_weather(city=city)

            forecast = weather_api.get_daily_forecast_from_3h(
                weather.location.latitude,
                weather.location.longitude
            )

        except WeatherAPIError as e:
            error = str(e)

    return render_template(
        "index.html",
        weather=weather,
        forecast=forecast,
        error=error
    )


@app.route("/location")
def location():

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    weather = weather_api.get_current_weather(
        lat=float(lat),
        lon=float(lon)
    )

    forecast = weather_api.get_daily_forecast_from_3h(
        float(lat),
        float(lon)
    )
    aqi = weather_api.get_air_quality(
    weather.location.latitude,
    weather.location.longitude
)

    return render_template(
    "index.html",
    weather=weather,
    forecast=forecast,
    aqi=aqi,
    error=error
)


if __name__ == "__main__":
    app.run(debug=True)