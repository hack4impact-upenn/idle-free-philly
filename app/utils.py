import re, datetime, csv, requests
from flask import url_for
from app.models import Location, Agency, IncidentReport


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


def parse_to_db(db, filename):
    city_default = ', philadelphia, pennsylvania, usa'
    viewport_default = '39.861204,-75.310357|40.138932,-74.928582'
    vehicle_id_index = 8
    license_plate_index = 9
    location_index = 4
    date_index = 0
    agency_index = 6
    picture_index = 13
    description_index = 11
    with open(filename, 'rb') as file:
        reader = csv.reader(file)
        columns = reader.next()
        for row in reader:
            address_text = row[location_index]
            # Viewport-biased geocoding using Google API
            url="https://maps.googleapis.com/maps/api/geocode/json"
            payload = {'address': address_text, 'bounds': viewport_default}
            r = requests.get(url, params=payload)
            coordinates = r.json()['results'][0]['geometry']['location']
            loc = Location(
                latitude=coordinates['lat'],
                longitude=coordinates['lng'],
                original_user_text=address_text)
            db.session.add(loc)
            date_format = "%m/%d/%Y %H:%M"
            start_time = datetime.datetime.strptime(row[date_index], date_format)
            end_time = datetime.datetime.strptime(row[date_index + 1], date_format)
            # Assign correct agency id
            agency_name = row[agency_index].rstrip().upper()
            if agency_name == 'OTHER':
                agency_name = row[agency_index + 1].rstrip().upper()
            a = Agency.query.filter_by(name=agency_name).first()
            if a is None:
                a = Agency(name=agency_name)
                a.is_public = True
                a.is_official = False
                db.session.add(a)
                db.session.commit()
            vehicle_id_text=row[vehicle_id_index].strip()
            if len(vehicle_id_text) is 0:
                vehicle_id_text = None
            license_plate_text=row[license_plate_index].strip()
            if len(license_plate_text) is 0:
                license_plate_text = None
            incident = IncidentReport(
                vehicle_id=vehicle_id_text,
                license_plate=license_plate_text,
                location=loc,
                date=start_time,
                duration=end_time - start_time,
                agency=a,
                picture_url=row[picture_index],
                description=row[description_index])
            db.session.add(incident)
            db.session.commit()
        return columns
