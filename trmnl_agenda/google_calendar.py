import datetime
import json
import logging
import os.path
import time
from collections import defaultdict
from functools import cmp_to_key
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def get_events(service, calendar_id: str, start_time: datetime, end_time: datetime):
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=start_time.isoformat(),
            timeMax=end_time.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])


def compare_events(event1, event2):
    start1 = event1["start"]
    start2 = event2["start"]

    if start1.get("date", None) is not None:
        return -1

    if start2.get("date", None) is not None:
        return 1

    start1_time = datetime.datetime.fromisoformat(start1.get("dateTime", None))
    start2_time = datetime.datetime.fromisoformat(start2.get("dateTime", None))

    if start1_time > start2_time:
        return 1

    if start1_time < start2_time:
        return -1

    return 0


def get_api_events(settings, days=14):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    skip_events = [skip.strip() for skip in settings.SKIP_EVENTS]
    try:
        creds = authenticate()
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        time_min = datetime.datetime.now(tz=datetime.timezone.utc)
        time_max = time_min + datetime.timedelta(days=days)

        events = []
        for calendar_id in settings.GOOGLE_CALENDAR_IDS:
            events.extend(get_events(service, calendar_id, time_min, time_max))

        if not events:
            return {}

        events = sorted(events, key=cmp_to_key(compare_events))

    except HttpError as error:
        print(f"An error occurred: {error}")
        return {}

    agenda = defaultdict(list)
    seen_events = set()
    for event in events:
        start_time = event["start"].get("dateTime", None)
        if start_time:
            start_time = datetime.datetime.fromisoformat(start_time)
            start_date = start_time.date().isoformat()
        else:
            start_date = event["start"].get("date", None)

        summary = event["summary"]
        if summary in skip_events:
            continue

        if start_time:
            am_pm = "a" if start_time.strftime("%p") == "AM" else "p"
            start_time = f"{start_time.hour % 12}:{start_time.minute:02d}{am_pm}"

            agenda_event = f"{start_time} {summary}"
        else:
            agenda_event = summary

        if agenda_event not in seen_events:
            agenda[start_date].append(agenda_event)
            seen_events.add(agenda_event)

    return agenda


def get_agenda(settings, max_age=600, force=False):
    data_dir = Path(__file__).parent.parent / "data"
    cache_file = data_dir / "google_calendar_agenda.json"
    cached_data = None
    expired = False
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            cached_data = json.load(f)
        modified_ago = time.time() - os.path.getmtime(cache_file)
        expired = modified_ago > max_age

    if cached_data is None or force or expired:
        logging.debug("Calling calendar api")
        data = get_api_events(settings)
    else:
        data = cached_data

    data_changed = data != cached_data
    if data_changed:
        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)

    return data, data_changed
