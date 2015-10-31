import re, datetime, csv, geocoder
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
    vehicle_id_index = 8
    license_plate_index = 9
    location_index = 4
    date_index = 0
    agency_index = 6
    picture_index = 13
    description_index = 11
    with open(filename, 'rb') as file:
        reader = csv.reader(file, delimiter=',')
        columns = reader.next()
        for row in reader:
            address_text = row[location_index]
            coordinates = geocoder.google(address_text + city_default).latlng
            # Try arcgis geocode implementation if Google fails
            if len(coordinates) == 0:
                coordinates = geocoder.arcgis(address_text + city_default).latlng
            loc = Location(
                latitude=coordinates[0],
                longitude=coordinates[1],
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
                a.is_public = False
                a.is_official = False
                db.session.add(a)
                db.session.commit()
            incident = IncidentReport(
                vehicle_id=row[vehicle_id_index],
                license_plate=row[license_plate_index],
                location=loc,
                date=start_time,
                duration=end_time - start_time,
                agency = a,
                picture_url=row[picture_index],
                description=row[description_index])
            db.session.add(incident)
            db.session.commit()
        return columns
