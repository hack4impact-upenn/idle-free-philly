import re
import requests
import time
import os

from flask import url_for, flash, current_app
from flask.ext.rq import get_queue
from imgurpython import ImgurClient
from datetime import timedelta
from redis import Redis
from rq_scheduler import Scheduler

from app import db


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
    if phone_number is None or phone_number == '':
        return None

    stripped = re.sub(r'\D', '', phone_number)
    if len(stripped) == 10:
        stripped = '1' + stripped
    stripped = '+' + stripped
    return stripped


def minutes_to_timedelta(minutes):
    """Use when creating new report."""
    return timedelta(minutes=minutes)


def parse_timedelta(duration):
    """Parse string into timedelta object"""
    h, m, s = duration.split(':')
    seconds = int(s) + 60 * int(m) + 3600 * int(h)
    return timedelta(seconds=seconds)


def flash_errors(form):
    """Show a list of all errors in form after trying to submit."""
    for field, errors in form.errors.items():
        for error in errors:
            flash("Error: %s - %s" % (
                getattr(form, field).label.text, error),
                'form-error')


def strip_non_alphanumeric_chars(input_string):
    """Strip all non-alphanumeric characters from the input."""
    stripped = re.sub('[\W_]+', '', input_string)
    return stripped


def geocode(address):
    """Viewport-biased geocoding using Google API.

    Returns a tuple of (latitude, longitude), (None, None) if geocoding fails.
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    payload = {
        'address': address,
        'bounds': current_app.config['VIEWPORT'],
        'key': current_app.config['GOOGLE_GEOCODE_KEY']
    }
    r = requests.get(url, params=payload)

    # Google's geocode api is limited to 10 requests a second
    if r.json()['status'] == 'OVER_QUERY_LIMIT':
        time.sleep(1)
        r = requests.get(url, params=payload)

    if r.json()['status'] == 'ZERO_RESULTS' or len(r.json()['results']) is 0:
        print r.json()
        return None, None
    else:
        coords = r.json()['results'][0]['geometry']['location']
        return coords['lat'], coords['lng']


def get_current_weather(location):
    """Given an app.models.Location object, returns the current weather at
    that location as a string."""

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


def upload_image(imgur_client_id, imgur_client_secret, app_name,
                 image_url=None, image_file_path=None):
    """Uploads an image to Imgur by the image's url or file_path. Returns the
    Imgur api response."""
    if image_url is None and image_file_path is None:
        raise ValueError('Either image_url or image_file_path must be '
                         'supplied.')
    client = ImgurClient(imgur_client_id, imgur_client_secret)
    title = '{} Image Upload'.format(current_app.config['APP_NAME'])

    description = 'This is part of an idling vehicle report on {}.'.format(
        current_app.config['APP_NAME'])

    if image_url is not None:
        result = client.upload_from_url(url=image_url, config={
            'title': title,
            'description': description,
        })
    else:
        result = client.upload_from_path(path=image_file_path, config={
            'title': title,
            'description': description,
        })
        os.remove(image_file_path)

    return result['link'], result['deletehash']


def delete_image(deletehash, imgur_client_id, imgur_client_secret):
    """Attempts to delete a specific image from Imgur using its deletehash."""
    client = ImgurClient(imgur_client_id, imgur_client_secret)

    client.delete_image(deletehash)


def get_rq_scheduler(app=current_app):
    conn = Redis(
        host=app.config['RQ_DEFAULT_HOST'],
        port=app.config['RQ_DEFAULT_PORT'],
        db=0,
        password=app.config['RQ_DEFAULT_PASSWORD']
    )
    return Scheduler(connection=conn)  # Get a scheduler for the default queue


def attach_image_to_incident_report(incident_report, image_job_id):
    """Attach the image uploaded by the job with image_job_id to the given
    incident_report."""
    link, deletehash = get_queue().fetch_job(image_job_id).result
    incident_report.picture_url = link
    incident_report.picture_deletehash = deletehash
    db.session.add(incident_report)
    db.session.commit()


def url_for_external(endpoint, **kwargs):
    """Get a full url (e.g. http:app.com/hello instead of just /hello"""
    if current_app.config['DOMAIN']:
        return current_app.config['DOMAIN'] + url_for(endpoint, **kwargs)
    else:
        # This will be correct, but may not be what you want.
        return url_for(endpoint, _external=True, **kwargs)
