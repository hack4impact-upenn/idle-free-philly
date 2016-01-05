import re
import requests
from flask import url_for, flash, current_app


def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    app.add_template_global(index_for_role)


def index_for_role(role):
    return url_for(role.index)


def parse_phone_number(phone_number):
    """Make phone number conform to E.164 (https://en.wikipedia.org/wiki/E.164)
    """
    stripped = re.sub(r'\D', '', phone_number)
    if len(stripped) == 10:
        stripped = '1' + stripped
    stripped = '+' + stripped
    return stripped


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("Error: %s - %s" % (
                getattr(form, field).label.text, error),
                'form-error')


def geocode(address):
    """Viewport-biased geocoding using Google API

    Returns a tuple of (latitude, longitude), (None, None) if geocoding fails
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    payload = {'address': address, 'bounds': current_app.config['VIEWPORT']}
    r = requests.get(url, params=payload)
    if r.json()['status'] is 'ZERO_RESULTS' or len(r.json()['results']) is 0:
        return None, None
    else:
        coords = r.json()['results'][0]['geometry']['location']
        return coords['lat'], coords['lng']


def get_current_weather(location):
    """TODO write docstring"""

    url = "http://api.openweathermap.org/data/2.5/weather"
    payload = {
        'APPID': current_app.config['OPEN_WEATHER_MAP_API_KEY'],
        'units': 'imperial',
        'lat': location.latitude,
        'lon': location.longitude,
    }
    r = requests.get(url, params=payload)
    response = r.json()
    weather_text = ''

    weather_key = response.get('weather')
    if weather_key is not None:
        weather_key = weather_key[0]
        if weather_key.get('description') is not None:
            weather_text += 'Description: {}\n'.format(
                weather_key['description'])

    main_key = response.get('main')
    if main_key is not None:
        if main_key.get('temp') is not None:
            weather_text += 'Temperature: {} degrees fahrenheit\n'.format(
                main_key['temp'])
        if main_key.get('pressure') is not None:
            weather_text += 'Atmospheric pressure: {} hPa\n'.format(
                main_key['pressure'])
        if main_key.get('humidity') is not None:
            weather_text += 'Humidity: {}%\n'.format(main_key['humidity'])

    wind_key = response.get('wind')
    if wind_key is not None:
        if wind_key.get('speed') is not None:
            weather_text += 'Wind speed: {} miles/hour\n'.format(
                wind_key['speed'])

    return weather_text.strip()
