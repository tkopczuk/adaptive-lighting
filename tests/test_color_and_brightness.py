import datetime as dt
import zoneinfo

import pytest
from astral import LocationInfo
from astral.location import Location
from homeassistant.components.adaptive_lighting.color_and_brightness import (
    SunEvent,
    SunEvents,
    SunLightSettings,
)

# Create a mock astral_location object
location = Location(LocationInfo())

LAT_LONG_TZS = [
    (52.379189, 4.899431, "Europe/Amsterdam"),
    (32.87336, -117.22743, "US/Pacific"),
    (60, 50, "GMT"),
    (60, 50, "UTC"),
]


@pytest.fixture(params=LAT_LONG_TZS)
def tzinfo_and_location(request):
    lat, long, timezone = request.param
    tzinfo = zoneinfo.ZoneInfo(timezone)
    location = Location(
        LocationInfo(
            name="name",
            region="region",
            timezone=timezone,
            latitude=lat,
            longitude=long,
        ),
    )
    return tzinfo, location


def _sun_light_settings(
    *,
    brightness_mode="default",
    inverse_brightness=False,
    min_brightness=1,
    max_brightness=43,
) -> SunLightSettings:
    return SunLightSettings(
        name="test",
        astral_location=location,
        adapt_until_sleep=False,
        max_brightness=max_brightness,
        max_color_temp=5500,
        min_brightness=min_brightness,
        min_color_temp=2000,
        sleep_brightness=7,
        sleep_rgb_or_color_temp="color_temp",
        sleep_color_temp=1000,
        sleep_rgb_color=(255, 56, 0),
        sunrise_time=dt.time(6, 0),
        min_sunrise_time=None,
        max_sunrise_time=None,
        sunset_time=dt.time(18, 0),
        min_sunset_time=None,
        max_sunset_time=None,
        brightness_mode_time_dark=dt.timedelta(minutes=15),
        brightness_mode_time_light=dt.timedelta(minutes=15),
        brightness_mode=brightness_mode,
        inverse_brightness=inverse_brightness,
        timezone=dt.UTC,
    )


@pytest.mark.parametrize("brightness_mode", ["default", "linear", "tanh"])
def test_inverse_brightness_flips_normal_curve(brightness_mode):
    normal = _sun_light_settings(
        brightness_mode=brightness_mode,
        inverse_brightness=False,
    )
    inverse = _sun_light_settings(
        brightness_mode=brightness_mode,
        inverse_brightness=True,
    )

    times = [
        dt.datetime(2022, 1, 1, 0, 0, tzinfo=dt.UTC),
        dt.datetime(2022, 1, 1, 5, 45, tzinfo=dt.UTC),
        dt.datetime(2022, 1, 1, 6, 0, tzinfo=dt.UTC),
        dt.datetime(2022, 1, 1, 6, 15, tzinfo=dt.UTC),
        dt.datetime(2022, 1, 1, 12, 0, tzinfo=dt.UTC),
        dt.datetime(2022, 1, 1, 17, 45, tzinfo=dt.UTC),
        dt.datetime(2022, 1, 1, 18, 0, tzinfo=dt.UTC),
        dt.datetime(2022, 1, 1, 18, 15, tzinfo=dt.UTC),
    ]

    for time in times:
        normal_pct = normal.brightness_pct(time, is_sleep=False)
        inverse_pct = inverse.brightness_pct(time, is_sleep=False)
        assert inverse_pct == pytest.approx(
            normal.min_brightness + normal.max_brightness - normal_pct,
        )


def test_inverse_brightness_reverses_min_max_values():
    inverse = _sun_light_settings(inverse_brightness=True)

    midnight = dt.datetime(2022, 1, 1, 0, 0, tzinfo=dt.UTC)
    noon = dt.datetime(2022, 1, 1, 12, 0, tzinfo=dt.UTC)

    assert inverse.brightness_pct(midnight, is_sleep=False) == pytest.approx(43)
    assert inverse.brightness_pct(noon, is_sleep=False) == pytest.approx(1)


def test_inverse_brightness_does_not_change_sleep_brightness():
    inverse = _sun_light_settings(inverse_brightness=True)

    noon = dt.datetime(2022, 1, 1, 12, 0, tzinfo=dt.UTC)

    assert inverse.brightness_pct(noon, is_sleep=True) == 7


def test_replace_time(tzinfo_and_location):
    tzinfo, location = tzinfo_and_location
    sun_events = SunEvents(
        name="test",
        astral_location=location,
        sunrise_time=None,
        min_sunrise_time=None,
        max_sunrise_time=None,
        sunset_time=None,
        min_sunset_time=None,
        max_sunset_time=None,
        timezone=tzinfo,
    )

    new_time = dt.time(5, 30)
    datetime = dt.datetime(2022, 1, 1)
    replaced_time_utc = sun_events._replace_time(datetime.date(), new_time)
    assert replaced_time_utc.astimezone(tzinfo).time() == new_time


def test_sunrise_without_offset(tzinfo_and_location):
    tzinfo, location = tzinfo_and_location

    sun_events = SunEvents(
        name="test",
        astral_location=location,
        sunrise_time=None,
        min_sunrise_time=None,
        max_sunrise_time=None,
        sunset_time=None,
        min_sunset_time=None,
        max_sunset_time=None,
        timezone=tzinfo,
    )
    date = dt.datetime(2022, 1, 1).date()
    result = sun_events.sunrise(date)
    assert result == location.sunrise(date)


def test_sun_position_no_fixed_sunset_and_sunrise(tzinfo_and_location):
    tzinfo, location = tzinfo_and_location
    sun_events = SunEvents(
        name="test",
        astral_location=location,
        sunrise_time=None,
        min_sunrise_time=None,
        max_sunrise_time=None,
        sunset_time=None,
        min_sunset_time=None,
        max_sunset_time=None,
        timezone=tzinfo,
    )
    date = dt.datetime(2022, 1, 1).date()
    sunset = location.sunset(date)
    position = sun_events.sun_position(sunset)
    assert position == 0
    sunrise = location.sunrise(date)
    position = sun_events.sun_position(sunrise)
    assert position == 0
    noon = location.noon(date)
    position = sun_events.sun_position(noon)
    assert position == 1
    midnight = location.midnight(date)
    position = sun_events.sun_position(midnight)
    assert position == -1


def test_sun_position_fixed_sunset_and_sunrise(tzinfo_and_location):
    tzinfo, location = tzinfo_and_location
    sun_events = SunEvents(
        name="test",
        astral_location=location,
        sunrise_time=dt.time(6, 0),
        min_sunrise_time=None,
        max_sunrise_time=None,
        sunset_time=dt.time(18, 0),
        min_sunset_time=None,
        max_sunset_time=None,
        timezone=tzinfo,
    )
    date = dt.datetime(2022, 1, 1).date()
    sunset = sun_events.sunset(date)
    position = sun_events.sun_position(sunset)
    assert position == 0
    sunrise = sun_events.sunrise(date)
    position = sun_events.sun_position(sunrise)
    assert position == 0
    noon, midnight = sun_events.noon_and_midnight(date)
    position = sun_events.sun_position(noon)
    assert position == 1
    position = sun_events.sun_position(midnight)
    assert position == -1


def test_noon_and_midnight(tzinfo_and_location):
    tzinfo, location = tzinfo_and_location
    sun_events = SunEvents(
        name="test",
        astral_location=location,
        sunrise_time=None,
        min_sunrise_time=None,
        max_sunrise_time=None,
        sunset_time=None,
        min_sunset_time=None,
        max_sunset_time=None,
        timezone=tzinfo,
    )
    date = dt.datetime(2022, 1, 1)
    noon, midnight = sun_events.noon_and_midnight(date)
    assert noon == location.noon(date)
    assert midnight == location.midnight(date)


def test_sun_events(tzinfo_and_location):
    tzinfo, location = tzinfo_and_location
    sun_events = SunEvents(
        name="test",
        astral_location=location,
        sunrise_time=None,
        min_sunrise_time=None,
        max_sunrise_time=None,
        sunset_time=None,
        min_sunset_time=None,
        max_sunset_time=None,
        timezone=tzinfo,
    )

    date = dt.datetime(2022, 1, 1)
    events = sun_events.sun_events(date)
    assert len(events) == 4
    assert (SunEvent.SUNRISE, location.sunrise(date).timestamp()) in events


def test_prev_and_next_events(tzinfo_and_location):
    tzinfo, location = tzinfo_and_location
    sun_events = SunEvents(
        name="test",
        astral_location=location,
        sunrise_time=None,
        min_sunrise_time=None,
        max_sunrise_time=None,
        sunset_time=None,
        min_sunset_time=None,
        max_sunset_time=None,
        timezone=tzinfo,
    )
    datetime = dt.datetime(2022, 1, 1, 10, 0)
    after_sunrise = sun_events.sunrise(datetime.date()) + dt.timedelta(hours=1)
    prev_event, next_event = sun_events.prev_and_next_events(after_sunrise)
    assert prev_event[0] == SunEvent.SUNRISE
    assert next_event[0] == SunEvent.NOON


def test_closest_event(tzinfo_and_location):
    tzinfo, location = tzinfo_and_location
    sun_events = SunEvents(
        name="test",
        astral_location=location,
        sunrise_time=None,
        min_sunrise_time=None,
        max_sunrise_time=None,
        sunset_time=None,
        min_sunset_time=None,
        max_sunset_time=None,
        timezone=tzinfo,
    )
    datetime = dt.datetime(2022, 1, 1, 6, 0)
    sunrise = sun_events.sunrise(datetime.date())
    event_name, ts = sun_events.closest_event(sunrise)
    assert event_name == SunEvent.SUNRISE
    assert ts == location.sunrise(sunrise.date()).timestamp()
