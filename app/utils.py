from flask import url_for
from app.models import IdlingIncident


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
    return url_for(role.name + '.index')


def parse_to_db(db, filename):
    import csv, geocoder
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
            print row
            address_text = row[location_index]
            # TODO: error handling for geocoder
            coordinates = geocoder.arcgis(address_text + city_default).latlng
            loc = Location(
                latitude=coordinates[0],
                longitude=coordinates[1],
                original_user_text=address_text)
            db.session.add(loc)
            incident = IdlingIncident(
                vehicle_id=row[vehicle_id_index],
                license_plate=row[license_plate_index],
                location=loc,
                date=row[date_index],
                # TODO: calculate duration interval from timestamps
                duration=0,
                picture_url=row[picture_index],
                description=row[description_index])
            db.session.add(incident)
        db.session.commit()
        return columns
