import re
from flask import url_for


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
    payload = {'address': address_text,
                'bounds': config['default'].VIEWPORT}
    r = requests.get(url, params=payload)
    if r.json()['status'] is 'ZERO_RESULTS' or len(r.json()['results']) is 0:
        return (None, None)
    else:
        coords = r.json()['results'][0]['geometry']['location']
        return (coords['lat'], coords['lng'])
