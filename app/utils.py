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
    vehicle_id_index = 7;
    location_index = 3;
    date_index = 0;
    agency_index = 6;
    picture_index = 13;
    description_index = 11;
    
    with open(filename, 'rb') as file:
        reader = csv.reader(file, delimiter=',')
        columns = reader.next()
        for row in reader:
            print row
            a = address=row[location_index]
            g = geocoder.arcgis(a + city_default).latlng
            l = Location(lat=g[0], long=g[1], address=a)
            i = IdlingIncident(vehicle_id=row[vehicle_id_index], l,
                date=row[date_index], agency=row[agency_index], picture=row[picture_index],
                description=row[description_index])
            db.session.add(i)
            db.session.commit()
        return columns
