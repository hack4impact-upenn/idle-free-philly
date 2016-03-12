from flask import render_template
from . import main
from app import models, db, reports
from app.models import IncidentReport, Agency, EditableHTML
from datetime import timedelta


@main.route('/', methods=['GET', 'POST'])
@main.route('/map', methods=['GET', 'POST'])
def index():
    form = reports.forms.IncidentReportForm()
    agencies = Agency.query.all()

    if form.validate_on_submit():
        l = models.Location(original_user_text=form.location.data,
                            latitude=form.latitude.data,
                            longitude=form.longitude.data)

        new_incident = models.IncidentReport(
            vehicle_id=form.vehicle_id.data,
            license_plate=form.license_plate.data,
            location=l,
            date=form.date.data,
            time=form.time.data,
            duration=timedelta(minutes=form.duration.data),
            agency=form.agency.data,
            description=form.description.data,
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
