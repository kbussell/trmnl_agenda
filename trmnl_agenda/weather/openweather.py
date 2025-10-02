from datetime import datetime

import requests

from .base import BaseWeatherProvider

MM_TO_INCH = 0.03937008

openweather_code_images = {
    "200": "tstorm",
    "201": "tstorm",
    "202": "tstorm",
    "210": "tstorm",
    "211": "tstorm",
    "212": "tstorm",
    "221": "tstorm",
    "230": "tstorm",
    "231": "tstorm",
    "232": "tstorm",
    "300": "drizzle",
    "301": "drizzle",
    "302": "drizzle",
    "310": "drizzle",
    "311": "drizzle",
    "312": "drizzle",
    "313": "drizzle",
    "314": "drizzle",
    "321": "drizzle",
    "500": "rain_light",
    "501": "rain",
    "502": "rain_heavy",
    "503": "rain_heavy",
    "504": "rain_heavy",
    "511": "freezing_rain",
    "520": "rain_light",
    "521": "rain",
    "522": "rain_heavy",
    "531": "rain_heavy",
    "600": "snow_light",
    "601": "snow",
    "602": "snow_heavy",
    "611": "ice_pellets",
    "612": "ice_pellets_light",
    "613": "ice_pellets",
    "615": "snow_light",
    "616": "snow",
    "620": "snow_light",
    "621": "snow",
    "622": "snow_heavy",
    "701": "fog_light",
    "741": "fog",
    "800": "clear_day",
    "801": "mostly_clear_day",
    "802": "partly_cloudy_day",
    "803": "mostly_cloudy",
    "804": "cloudy",
}


class OpenWeatherMapProvider(BaseWeatherProvider):
    def get_weather_api_data(self):
        settings = self.settings

        params = {
            "appid": settings.OPENWEATHER_API_KEY,
            "lat": settings.LAT,
            "lon": settings.LON,
            "exclude": "minutely,hourly",
            "units": settings.WEATHER_UNITS,
        }

        response = requests.get("https://api.openweathermap.org/data/3.0/onecall", params=params)
        response.raise_for_status()

        return response.json()

    def format_data(self, data=None) -> dict:
        weather = {}
        for day in data["daily"]:
            day_date = datetime.fromtimestamp(day["dt"]).date().isoformat()
            weather_code = str(day["weather"][0]["id"])

            convert_to_inches = self.settings.WEATHER_UNITS == "imperial"

            rain = day.get("rain", 0)
            if convert_to_inches:
                rain = round(rain * MM_TO_INCH, 2)

            rain = f'{rain}"' if rain > 0 else None

            snow = day.get("snow", 0)
            if convert_to_inches:
                snow = round(snow * MM_TO_INCH, 2)
            snow = f'{snow}"' if snow > 0 else None

            weather[day_date] = {
                "img": openweather_code_images.get(weather_code, ""),
                "l": f"{round(day['temp']['min'])}°",
                "h": f"{round(day['temp']['max'])}°",
                "rain": rain or "",
                "snow": snow or "",
            }

        return weather
