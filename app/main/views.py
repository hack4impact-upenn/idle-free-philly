from flask import render_template
from ..models import EditableHTML
from . import main
from app import models, db
from forms import NewIncidentForm
from app.models import IncidentReport, Agency
from datetime import timedelta


@main.route('/')
@main.route('/map')
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
