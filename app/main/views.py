from flask import render_template
from ..models import EditableHTML, IncidentReport
from . import main
<<<<<<< HEAD
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
=======


@main.route('/')
@main.route('/map')
def index():
    """Get information on all Incident Reports in the db, and
    pass to map.html
    """
    return render_template('main/map.html',
>>>>>>> c2c121c37b865a8aa4c108eccf9d4d473df17be2
                           incident_reports=IncidentReport.query.all())


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('main/about.html',
                           editable_html_obj=editable_html_obj)


@main.route('/faq')
def faq():
    editable_html_obj = EditableHTML.get_editable_html('faq')
    return render_template('main/faq.html',
                           editable_html_obj=editable_html_obj)
