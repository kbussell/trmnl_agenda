import json
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseWeatherProvider:
    def __init__(self, settings):
        self.settings = settings

    def get_weather_data(self, max_age=600, force=False):
        settings = self.settings

        cached_data = None
        data_dir = Path(__file__).parent.parent.parent / "data"
        cache_file = data_dir / f"{settings.WEATHER_PROVIDER}_{settings.LAT}_{settings.LON}.json"
        expired = False
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                cached_data = json.load(f)

            modified_ago = time.time() - os.path.getmtime(cache_file)
            expired = modified_ago > max_age

        if cached_data is None or force or expired:
            logger.info("%s: Calling weather api", self.__class__.__name__)
            data = self.get_weather_api_data()
        else:
            data = cached_data

        data_changed = data != cached_data
        if data_changed:
            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2)

        return self.format_data(data), data_changed

    def get_weather_api_data(self):
        raise NotImplementedError()

    def format_data(self, data):
        raise NotImplementedError()


def get_weather_data(settings, max_age=3000, force=False):
    from .openweather import OpenWeatherMapProvider
    from .tomorrowio import TomorrowIOProvider

    if settings.WEATHER_PROVIDER == "openweathermap":
        provider = OpenWeatherMapProvider(settings)
    elif settings.WEATHER_PROVIDER == "tomorrow.io":
        provider = TomorrowIOProvider(settings)
    else:
        raise ValueError(f"Unknown weather provider {settings.WEATHER_PROVIDER}")

    return provider.get_weather_data(max_age, force)
