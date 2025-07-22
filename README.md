# TRMNL Agenda Plugin

## Prerequisites

### Tools

* uv - https://docs.astral.sh/uv/getting-started/installation/
* mise - https://mise.jdx.dev/installing-mise.html
* docker - https://docs.docker.com/engine/install/

### Google OAuth credentials

You need a client ID for this app to connect to Google Calendar via [OAuth 2.0](https://developers.google.com/identity/protocols/oauth2/).

For this, you'll need a Google Cloud account.

* https://console.cloud.google.com/auth/clients/create
    * Application type: Desktop app
    * Name: TRMNL Google connector (or something else descirptive)
    * Click Create
    * "Download JSON" and save it into data/oauth_client_secret.json

* `mise run google_auth`
  * And complete the authentication flow with your browser
  * You should now have a `google_auth_token.json` file in `data/`

# API key for weather forecast provider

This plugin supports [OpenWeather](https://openweathermap.org/) and [tomorrow.io](https://www.tomorrow.io/). (I started
with tomorrow.io, but their free plan only has daily forecasts for the next 5 days, so I switched to using OpenWeather.)

Sign up with one of those providers and get an API key. See below for how to configure it

## Setup

Create a `.env` file instead with the following contents:
```
GOOGLE_CALENDAR_IDS=<comma separated list of google calendar IDs>
SKIP_EVENTS=<comma separated list of calendar event summaries to exclude from the agenda>

WEATHER_PROVIDER=<"openweathermap" or "tomorrow.io">
OPENWEATHER_API_KEY=<your openweather API key (if using openweather)>
TOMORROW_IO_API_KEY=<your tomorrow.io API key (if using tomorrow.io)>
LAT=<latitude>
LON=<longitude>

TRMNL_WEBHOOK_URL=<trmnl webhook URL for your plugin>
```

## Local development

* `mise run serve` to run the trmnlp development server
* `python trmnl_agenda/main.py` to publish updated data to trmnlp
