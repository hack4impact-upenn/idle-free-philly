import re
import requests
import csv
import functools
from datetime import datetime
from flask import url_for, current_app
from app.models import Location, Agency, IncidentReport
from app.main.forms import IncidentReportForm


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


def geocode(address):
    """Viewport-biased geocoding using Google API.

    Returns a tuple of (latitude, longitude), (None, None) if geocoding fails.
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    payload = {'address': address, 'bounds': current_app.config['VIEWPORT']}
    r = requests.get(url, params=payload)
    if r.json()['status'] is 'ZERO_RESULTS' or len(r.json()['results']) is 0:
        return None, None
    else:
        coords = r.json()['results'][0]['geometry']['location']
        return coords['lat'], coords['lng']


def parse_to_db(db, filename):
    """Reads a csv and imports the data into a database."""
    # The indices in the csv of different data
    vehicle_id_index = 8
    license_plate_index = 9
    location_index = 4
    date_index = 0
    agency_index = 6
    picture_index = 13
    description_index = 11

    validator_form = IncidentReportForm()

    with open(filename, 'rb') as csv_file:
        reader = csv.reader(csv_file)
        columns = reader.next()

        for i, row in enumerate(reader, start=2):  # i is the row number
            address_text = row[location_index]
            coords = geocode(address_text)

            # Ignore rows that do not have correct geocoding
            if coords[0] is None or coords[1] is None:
                print_error(i, 'Failed to geocode "{:s}"'.format(address_text))

            # Insert correctly geocoded row to database
            else:
                loc = Location(
                    latitude=coords[0],
                    longitude=coords[1],
                    original_user_text=address_text)
                db.session.add(loc)
                date_format = "%m/%d/%Y %H:%M"
                time1 = datetime.strptime(row[date_index], date_format)
                time2 = datetime.strptime(row[date_index+1], date_format)
                duration = time2 - time1

                # Assign correct agency id
                agency_name = row[agency_index].rstrip()
                if agency_name.upper() == 'OTHER':
                    agency_name = row[agency_index + 1].rstrip()
                agency = Agency.get_agency_by_name(agency_name)

                # Create new agency object if not in database
                if agency is None:
                    agency = Agency(name=agency_name)
                    agency.is_public = True
                    agency.is_official = False
                    db.session.add(agency)
                    db.session.commit()
                vehicle_id_text = row[vehicle_id_index].strip()

                if len(vehicle_id_text) is 0:
                    vehicle_id_text = None
                license_plate_text = row[license_plate_index].strip()

                if len(license_plate_text) is 0:
                    license_plate_text = None

                # Validate all the fields
                validate_field = functools.partial(
                    validate_field_partial,
                    form=validator_form,
                    row_number=i
                )

                kosher = True

                kosher = kosher and validate_field(
                    field=validator_form.vehicle_id,
                    data=vehicle_id_text
                )

                kosher = kosher and validate_field(
                    field=validator_form.license_plate,
                    data=license_plate_text
                )

                kosher = kosher and validate_field(
                    field=validator_form.date,
                    data=time1
                )

                kosher = kosher and validate_field(
                    field=validator_form.duration,
                    data=duration
                )

                kosher = kosher and validate_field(
                    field=validator_form.agency,
                    data=agency
                )

                kosher = kosher and validate_field(
                    field=validator_form.description,
                    data=row[description_index]
                )

                kosher = kosher and validate_field(
                    field=validator_form.picture_url,
                    data=row[picture_index]
                )

                if kosher:
                    incident = IncidentReport(
                        vehicle_id=vehicle_id_text,
                        license_plate=license_plate_text,
                        location=loc,
                        date=time1,
                        duration=duration,
                        agency=agency,
                        picture_url=row[picture_index],
                        description=row[description_index])
                    db.session.add(incident)
                    db.session.commit()

        return columns


def validate_field_partial(field, data, form, row_number):
    """TODO: docstring"""
    field.data = data
    field.raw_data = data
    validated = field.validate(form)

    if not validated:
        for error in field.errors:
            print_error(row_number, error)

    return validated


def print_error(row_number, error_message):
    """TODO: docstring"""
    print 'Row {:d}: {}'.format(row_number, error_message)
