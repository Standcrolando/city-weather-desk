import unittest
from unittest.mock import patch

import requests

from app import GEOCODING_URL, WEATHER_URL, app


class WeatherApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def fake_get_json(self, url, params):
        if url == GEOCODING_URL:
            return {
                "results": [{
                    "name": "Test City",
                    "country": "Test Country",
                    "admin1": "Test Region",
                    "latitude": 25.0,
                    "longitude": 121.0,
                }]
            }
        if url == WEATHER_URL:
            return {
                "timezone": "Asia/Taipei",
                "current": {
                    "temperature_2m": 25,
                    "relative_humidity_2m": 60,
                    "apparent_temperature": 26,
                    "weather_code": 0,
                    "wind_speed_10m": 5,
                    "wind_direction_10m": 90,
                    "wind_gusts_10m": 8,
                    "visibility": 10000,
                    "surface_pressure": 1012,
                },
                "current_units": {
                    "temperature_2m": "°C",
                    "relative_humidity_2m": "%",
                    "wind_speed_10m": "km/h",
                    "wind_direction_10m": "°",
                    "wind_gusts_10m": "km/h",
                    "visibility": "m",
                    "surface_pressure": "hPa",
                },
                "daily": {
                    "time": ["2026-08-20"],
                    "weather_code": [0],
                    "temperature_2m_max": [30],
                    "temperature_2m_min": [22],
                    "temperature_2m_mean": [26],
                    "uv_index_max": [5],
                    "sunrise": ["2026-08-20T05:30"],
                    "sunset": ["2026-08-20T18:30"],
                },
                "daily_units": {"temperature_2m_max": "°C"},
            }
        raise AssertionError(f"Unexpected URL: {url}")

    @patch("app.get_json")
    def test_weather_returns_detailed_data(self, get_json):
        get_json.side_effect = self.fake_get_json
        response = self.client.get("/api/weather?city=測試城市")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["current"]["wind_direction_text"], "東")
        self.assertEqual(data["current"]["visibility"], 10000)
        self.assertEqual(data["daily"][0]["mean"], 26)
        self.assertIn("next_full_moon", data["astronomy"])

    @patch("app.get_json")
    def test_multilingual_city_alias_is_normalized(self, get_json):
        get_json.side_effect = self.fake_get_json
        response = self.client.get("/api/weather?city=서울")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_json.call_args_list[0].args[1]["name"], "Seoul")

    def test_validation_and_api_404(self):
        self.assertEqual(self.client.get("/api/weather").status_code, 400)
        response = self.client.get("/api/unknown")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    @patch("app.get_json", side_effect=requests.Timeout)
    def test_weather_service_error_returns_json(self, get_json):
        response = self.client.get("/api/weather?city=服務錯誤城市")
        self.assertEqual(response.status_code, 502)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
