from flask import render_template, request, flash
from . import main
from app import models, db
from forms import NewIncidentForm
from app.models import IncidentReport


@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/map', methods =['GET','POST'])
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

    """Create a new form."""
    form = NewIncidentForm()
    current_loc = "testing123"
    if form.validate_on_submit():
        from datetime import timedelta
        from faker import Faker
        from random import seed, choice, randint
        fake = Faker()

        current_address = ""
        address = ""
        l = models.Location(original_user_text =form.location.data, latitude= form.latitude.data,
                            longitude= form.longitude.data)
        agencies = models.Agency.query.all()
        new_incident = models.IncidentReport(
            vehicle_id=form.vehicle_ID.data,
            license_plate=form.license_plate_number.data,
            location=l,
            date=fake.date_time_between(start_date="-1y", end_date="now"),
            duration=timedelta(minutes=randint(1, 30)),
            agency=choice(agencies),
            picture_url=fake.image_url(),
            description=form.notes.data,
        )
        db.session.add(new_incident)
        db.session.commit()
    return render_template('main/map.html', incident_reports=IncidentReport.query.all())
