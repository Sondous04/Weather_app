import pytest
import app as weather_app

SAMPLE = {
    "city": {"name": "London"},
    "list": [{"main": {"temprature": 287.35, "temprature_unit": "K",
                       "humidity": 70},
              "weather": [{"description": "light rain"}]}],
}


@pytest.fixture
def client():
    return weather_app.app.test_client()


def test_parse_weather():
    result = weather_app.parse_weather(SAMPLE)
    assert result == {"city": "London", "temp": 14.2,
                      "humidity": 70, "description": "light rain"}


def test_parse_empty_response():
    with pytest.raises(ValueError):
        weather_app.parse_weather({"list": []})


def test_empty_input(client):
    r = client.get("/?city=")
    assert b"Please enter a city" in r.data


def test_valid_city(client, monkeypatch):
    monkeypatch.setattr(weather_app, "fetch_weather", lambda c: SAMPLE)
    r = client.get("/?city=London,GB")
    assert b"light rain" in r.data and b"14.2" in r.data


def test_invalid_city(client, monkeypatch):
    def boom(c):
        raise Exception("404")
    monkeypatch.setattr(weather_app, "fetch_weather", boom)
    r = client.get("/?city=asdfgh")
    assert b"Could not fetch weather" in r.data


def test_health(client):
    assert client.get("/health").json == {"status": "ok"}
