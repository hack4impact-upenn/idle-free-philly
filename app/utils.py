import re
import requests
from flask import url_for, current_app
from imgurpython import ImgurClient


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


# Viewport-biased geocoding using Google API
# Returns a tuple of (latitude, longitude), (None, None) if geocoding fails
def geocode(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    payload = {'address': address, 'bounds': current_app.config['VIEWPORT']}
    r = requests.get(url, params=payload)
    if r.json()['status'] is 'ZERO_RESULTS' or len(r.json()['results']) is 0:
        return None, None
    else:
        coords = r.json()['results'][0]['geometry']['location']
        return coords['lat'], coords['lng']


def upload_image(image_url=None, image_file_path=None, title=None,
                 description=None):
    """Uploads an image to Imgur by the image's url or file_path. Returns the
    Imgur api response."""
    if image_url is None and image_file_path is None:
        raise ValueError('Either image_url or image_file_path must be '
                         'supplied.')
    client = ImgurClient(current_app.config['IMGUR_CLIENT_ID'],
                         current_app.config['IMGUR_CLIENT_SECRET'])
    if title is None:
        title = '{} Image Upload'.format(current_app.config['APP_NAME'])

    if description is None:
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

    return result['link'], result['deletehash']
