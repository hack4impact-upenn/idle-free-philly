from datetime import timedelta, datetime

from flask import render_template, current_app
from flask.ext.rq import get_queue
from werkzeug import secure_filename

from . import main
from app import models, db
from app.reports.forms import IncidentReportForm
from app.models import IncidentReport, Agency, EditableHTML
from app.utils import upload_image, attach_image_to_incident_report, geocode


@main.route('/', methods=['GET', 'POST'])
@main.route('/map', methods=['GET', 'POST'])
def index():
    form = IncidentReportForm()
    agencies = Agency.query.all()

    if form.validate_on_submit():

        # If geocode happened client-side, it's not necessary to geocode again.
        lat, lng = form.latitude.data, form.longitude.data
        if not lat or not lng:
            lat, lng = geocode(form.location.data)

        l = models.Location(original_user_text=form.location.data,
                            latitude=lat,
                            longitude=lng)

        agency = form.agency.data
        if agency is None:
            agency = Agency(name=form.other_agency.data, is_official=False,
                            is_public=False)

        new_incident = models.IncidentReport(
            vehicle_id=form.vehicle_id.data,
            license_plate=form.license_plate.data,
            location=l,
            date=datetime.combine(form.date.data, form.time.data),
            duration=timedelta(minutes=form.duration.data),
            agency=agency,
            description=form.description.data,
        )
        db.session.add(new_incident)
        db.session.commit()

        if form.picture_file.data.filename:
            filepath = secure_filename(form.picture_file.data.filename)
            form.picture_file.data.save(filepath)

            image_job_id = get_queue().enqueue(
                upload_image,
                imgur_client_id=current_app.config['IMGUR_CLIENT_ID'],
                imgur_client_secret=current_app.config['IMGUR_CLIENT_SECRET'],
                app_name=current_app.config['APP_NAME'],
                image_file_path=filepath
            ).id

            get_queue().enqueue(
                attach_image_to_incident_report,
                depends_on=image_job_id,
                incident_report=new_incident,
                image_job_id=image_job_id,
            )

    # pre-populate form
    form.date.default = datetime.now()
    form.time.default = datetime.now()
    form.process()

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
