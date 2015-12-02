from flask import render_template
from . import main
from app import models, db
from forms import NewIncidentForm
from app.models import IncidentReport, Agency
from datetime import timedelta


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/map', methods=['GET', 'POST'])
def get_map():
    form = NewIncidentForm()
    agencies = Agency.query.all()

    if form.validate_on_submit():
        l = models.Location(original_user_text=form.location.data,
                            latitude=form.latitude.data,
                            longitude=form.longitude.data)

        new_incident = models.IncidentReport(
            vehicle_id=form.vehicle_ID.data,
            license_plate=form.license_plate_number.data,
            location=l,
            date=form.date.data,
            duration=timedelta(minutes=form.idling_duration.data),
            agency=form.agency.data,
            description=form.notes.data,
        )
        db.session.add(new_incident)
        db.session.commit()
    return render_template('main/map.html',
                           agencies=agencies,
                           form=form,
                           incident_reports=IncidentReport.query.all())
