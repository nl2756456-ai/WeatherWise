from flask import Flask, render_template, request
from weather_api import WeatherAPI, WeatherAPIError

app = Flask(__name__)

weather_api = WeatherAPI()

recent_searches = []


def format_hourly_data(hourly):
    if not hourly:
        return []

    return [
        {
            "time": h["time"].strftime("%I %p"),
            "temp": h["temp"]
        }
        for h in hourly
    ]


@app.route("/", methods=["GET", "POST"])
def home():

    weather = None
    forecast = None
    hourly = None
    aqi = None
    error = None

    if request.method == "POST":

        city = request.form.get("city", "").strip()

        if city:

            try:

                weather = weather_api.get_current_weather(
                    city=city
                )

                # Recent searches
                if weather.location.city not in recent_searches:
                    recent_searches.insert(
                        0,
                        weather.location.city
                    )

                recent_searches[:] = recent_searches[:5]


                # Forecast
                forecast = weather_api.get_daily_forecast_from_3h(
                    weather.location.latitude,
                    weather.location.longitude
                )


                # Hourly
                hourly = weather_api.get_hourly_forecast(
                    weather.location.latitude,
                    weather.location.longitude
                )


                # AQI
                aqi = weather_api.get_air_quality(
                    weather.location.latitude,
                    weather.location.longitude
                )


            except WeatherAPIError as e:

                error = str(e)


    hourly_data = format_hourly_data(hourly)


    return render_template(
        "index.html",

        weather=weather,

        forecast=forecast,

        hourly=hourly,

        hourly_data=hourly_data,

        aqi=aqi,

        error=error,

        recent_searches=recent_searches
    )


@app.route("/location")
def location():

    lat = request.args.get("lat")
    lon = request.args.get("lon")


    if not lat or not lon:

        return "Location coordinates are missing.", 400


    try:

        lat = float(lat)
        lon = float(lon)


        weather = weather_api.get_current_weather(
            lat=lat,
            lon=lon
        )


        forecast = weather_api.get_daily_forecast_from_3h(
            lat,
            lon
        )


        hourly = weather_api.get_hourly_forecast(
            lat,
            lon
        )


        aqi = weather_api.get_air_quality(
            lat,
            lon
        )


        hourly_data = format_hourly_data(hourly)


        return render_template(
            "index.html",

            weather=weather,

            forecast=forecast,

            hourly=hourly,

            hourly_data=hourly_data,

            aqi=aqi,

            error=None,

            recent_searches=recent_searches
        )


    except WeatherAPIError as e:

        return render_template(
            "index.html",

            weather=None,

            forecast=None,

            hourly=None,

            hourly_data=[],

            aqi=None,

            error=str(e),

            recent_searches=recent_searches
        )


if __name__ == "__main__":
    app.run(debug=True)