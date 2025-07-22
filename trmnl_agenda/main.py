import argparse
import logging
import os
from datetime import date, datetime, timedelta

import requests
import settings
import yaml
from google_calendar import get_agenda
from weather import get_weather_data

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

SKIP_EVENTS = ["Hold: grain", "Patch"]

MAX_HEIGHT_FULL = 480
MAX_HEIGHT_HALF = 225


def filter_events(events):
    return [event for event in events if event[1] not in SKIP_EVENTS]


def extra_events(count):
    if count <= 0:
        return None

    return f"{count} more event{'s' if count > 1 else ''}..."


def get_payload(max_age=600, force=False):
    weather_data, weather_data_changed = get_weather_data(settings, max_age, force)
    calendar_data, calendar_data_changed = get_agenda(settings, max_age, force)

    data_dates = set(weather_data.keys())
    data_dates.update(calendar_data.keys())
    data_dates = sorted(data_dates)

    days = []

    space_taken = 0
    days_full = 0
    days_half = 0

    cur_date = date.today()
    skip = False
    max_event_count = 0
    while cur_date.isoformat() <= data_dates[-1]:
        weather = weather_data.get(cur_date.isoformat(), None)
        events = calendar_data.get(cur_date.isoformat(), [])
        event_count = len(events) if events else 0
        max_event_count = max(max_event_count, event_count)

        if weather or events:
            space_taken += 60 if event_count == 3 else 40
            if space_taken <= MAX_HEIGHT_HALF:
                days_half += 1
            if space_taken <= MAX_HEIGHT_FULL:
                days_full += 1

            days.append(
                {
                    "day": cur_date.strftime("%a"),
                    "date": f"{cur_date.month}/{cur_date.day}",
                    "events": events,
                    "weather": weather,
                    "skip": skip,
                    "extra1": extra_events(event_count - 2),
                    "extra2": extra_events(event_count - 5),
                }
            )
            skip = False
        else:
            skip = True

        cur_date += timedelta(days=1)

    data = {
        "days": days,
        "two_cols": True if max_event_count > 3 else False,
        "days_full": days_full,
        "days_half": days_half,
    }

    return data, calendar_data_changed or weather_data_changed


def post_to_trmnl(data):
    if not settings.WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL not set")

    logger.info("Calling TRMNL webhook")
    response = requests.post(
        settings.WEBHOOK_URL,
        json={
            "merge_variables": data,
        },
    )
    logger.info(response.json())
    return response


def render_termnlp_yaml(data):
    output = {
        "watch": ["src", ".trmnlp.yml"],
        "time_zone": "America/Los_Angeles",
        "variables": {
            **data,
            "timestamp": datetime.now().isoformat(),
            "trmnl": {
                "plugin_settings": {
                    "instance_name": "Week Agenda",
                    "strategy": "webhook",
                    "dark_mode": "no",
                    "polling_headers": "",
                    "polling_url": "",
                }
            },
        },
    }

    base_dir = os.path.dirname(os.path.dirname(__file__))

    with open(os.path.join(base_dir, "TRMNL/.trmnlp.yml"), "w") as f:
        yaml.dump(output, f)


def main():
    parser = argparse.ArgumentParser(description="Create a css file of weather icons")
    parser.add_argument("--max-age", type=int, help="Max cache age", default=600)
    parser.add_argument("-f", "--force", action="store_true", help="Force reload data")
    parser.add_argument("--live", action="store_true", help="Live mode. Call TRMNL webhook")
    args = parser.parse_args()

    data, data_changed = get_payload(args.max_age, args.force)
    if args.live:
        post_to_trmnl(data)
    else:
        render_termnlp_yaml(data)


if __name__ == "__main__":
    main()
