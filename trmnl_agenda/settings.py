from pathlib import Path

from decouple import Csv, config

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

GOOGLE_CALENDAR_IDS = config("GOOGLE_CALENDAR_IDS", cast=Csv(str), default=[])
SKIP_EVENTS = config("SKIP_EVENTS", cast=Csv(str), default=[])

WEATHER_PROVIDER = config("WEATHER_PROVIDER", default="openweathermap")
OPENWEATHER_API_KEY = config("OPENWEATHER_API_KEY")

TOMORROW_IO_API_KEY = config("TOMORROW_IO_API_KEY")
WEATHER_UNITS = config("WEATHER_UNITS", default="imperial")
LAT = config("LAT")
LON = config("LON")

TRMNL_WEBHOOK_URL = config("TRMNL_WEBHOOK_URL")
