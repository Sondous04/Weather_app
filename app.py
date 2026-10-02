import os
import requests
from flask import Flask, render_template_string, request

API_HOST = "weather-api167.p.rapidapi.com"
API_URL = f"https://{API_HOST}/api/weather/forecast"

app = Flask(__name__)

PAGE = """
<!doctype html>
<title>Weather</title>
<style>
 body{font-family:sans-serif;max-width:420px;margin:60px auto;padding:0 16px}
 input,button{padding:8px;font-size:16px}
 .card{margin-top:20px;padding:16px;border:1px solid #ddd;border-radius:8px}
 .err{color:#b00020;margin-top:16px}
</style>
<h1>la meteo</h1>
<form method="get" action="/">
  <input name="city" placeholder="e.g. London,GB" value="{{ city or '' }}">
  <button type="submit">Search</button>
</form>
{% if error %}<p class="err">{{ error }}</p>{% endif %}
{% if weather %}
<div class="card">
  <h2>{{ weather.city }}</h2>
  <p>Temperature: {{ weather.temp }} &deg;C</p>
  <p>Conditions: {{ weather.description }}</p>
  <p>Humidity: {{ weather.humidity }}%</p>
</div>
{% endif %}
"""


def fetch_weather(city):
    key = os.environ.get("RAPIDAPI_KEY")
    if not key:
        raise RuntimeError("RAPIDAPI_KEY is not set")
    resp = requests.get(
        API_URL,
        headers={"x-rapidapi-key": key, "x-rapidapi-host": API_HOST},
        params={
            "place": city, "cnt": 1,
            "units": "standard", "lang": "en", "mode": "json",
            "type": "three_hour",
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def parse_weather(data):
    items = data.get("list") or []
    if not items:
        raise ValueError("No weather data found for that city.")
    first = items[0]
    main = first.get("main", {})
    weather = (first.get("weather") or [{}])[0]
    # The API spells it "temprature" and returns Kelvin with units=standard
    temp = main.get("temprature", main.get("temp"))
    if temp is not None and main.get("temprature_unit", "K") == "K":
        temp = round(temp - 273.15, 1)
    return {
        "city": data.get("city", {}).get("name", "Unknown"),
        "temp": temp,
        "humidity": main.get("humidity"),
        "description": weather.get("description", "n/a"),
    }


@app.route("/")
def index():
    city = request.args.get("city", "").strip()
    weather = error = None
    if "city" in request.args:
        if not city:
            error = "Please enter a city."
        else:
            try:
                weather = parse_weather(fetch_weather(city))
            except ValueError as e:
                error = str(e)
            except Exception:
                error = "Could not fetch weather. Check the city name and try again."
    return render_template_string(PAGE, city=city, weather=weather, error=error)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
