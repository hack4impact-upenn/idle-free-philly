from flask import render_template
from . import main
from app import models, db

@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/map')
def get_map():
    #Get information on all Incident Reports in the db, and pass to
    #map.html
    vehicle_ids = []
    license_plates = []
    latitudes = []
    longitudes = []
    dates = []
    durations = []
    agencies = []
    pictures = []
    descriptions = []

    for ir in models.IncidentReport.query.all():
        vehicle_ids.append(str(ir.vehicle_id))
        license_plates.append(str(ir.license_plate))

#Pass latitudes, longitudes as floats so they can be used to fix
        #locations of map markers
        latitudes.append(float((ir.location).latitude))
        longitudes.append(float((ir.location).longitude))
        dates.append(str(ir.date))
        durations.append(str(ir.duration))
        print('vehicle id:', ir.vehicle_id)
        agencies.append(str(ir.agency.name))
        pictures.append(ir.picture_url)
        descriptions.append(str(ir.description))

    return render_template('main/map.html', vehicle_ids=vehicle_ids, license_plates=license_plates, latitudes=latitudes, longitudes=longitudes, dates=dates, durations=durations, agencies=agencies, pictures=pictures, descriptions=descriptions)
