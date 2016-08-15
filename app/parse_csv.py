import csv
import functools
from datetime import datetime
from app.utils import geocode, strip_non_alphanumeric_chars
from app.models import Location, Agency, IncidentReport
from app.reports.forms import IncidentReportForm


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

                time1, time2 = parse_start_end_time(date_index, row)

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
                license_plate_text = row[license_plate_index].strip()

                # If the license plate is too short, just ignore it
                if len(strip_non_alphanumeric_chars(license_plate_text)) < 3:
                    license_plate_text = ''

                # Validate all the fields
                validate_field = functools.partial(
                    validate_field_partial,
                    form=validator_form,
                    row_number=i
                )

                errors = 0

                if not validate_field(
                    field=validator_form.vehicle_id,
                    data=vehicle_id_text
                ):
                    errors += 1

                if not validate_field(
                    field=validator_form.description,
                    data=row[description_index]
                ):
                    errors += 1

                if not validate_field(
                    field=validator_form.picture_url,
                    data=row[picture_index]
                ):
                    errors += 1

                if errors == 0:
                    vehicle_id_text = strip_non_alphanumeric_chars(
                        vehicle_id_text)
                    license_plate_text = strip_non_alphanumeric_chars(
                        license_plate_text)

                    incident = IncidentReport(
                        vehicle_id=vehicle_id_text if len(vehicle_id_text) > 0
                        else None,
                        license_plate=license_plate_text if
                        len(license_plate_text) > 0 else None,
                        location=loc,
                        date=time1,
                        duration=time2 - time1,
                        agency=agency,
                        picture_url=row[picture_index],
                        description=row[description_index],
                        send_email_upon_creation=False,
                    )
                    db.session.add(incident)

        db.session.commit()
        return columns


def parse_start_end_time(date_index, row):
    for date_format in ['%m/%d/%Y %H:%M', '%m/%d/%y %H:%M']:
        try:
            time1 = datetime.strptime(row[date_index], date_format)
        except ValueError:
            pass

        try:
            time2 = datetime.strptime(row[date_index + 1],
                                      date_format)
        except ValueError:
            pass

    return time1, time2


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
