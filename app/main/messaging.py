import string
import itertools
from flask import request, make_response, current_app, url_for
from flask.ext.rq import get_queue
from . import main
from .. import db
from ..utils import geocode, upload_image, get_rq_scheduler
from ..models import Agency, IncidentReport, Location
from ..main.forms import IncidentReportForm
from datetime import datetime, timedelta
import twilio.twiml
from twilio.rest import TwilioRestClient


@main.route('/report_incident', methods=['GET'])
def handle_message():
    body, message_sid, twilio_hosted_media_url = get_request_values()

    twiml = twilio.twiml.Response()

    # Retrieve incident cookies
    step = int(request.cookies.get('messagecount', 0))
    vehicle_id = str(request.cookies.get('vehicle_id', ''))
    agency_name = str(request.cookies.get('agency_name', ''))
    license_plate = str(request.cookies.get('license_plate', ''))
    duration = int(request.cookies.get('duration', 0))
    description = str(request.cookies.get('description', ''))
    location = str(request.cookies.get('location', ''))
    picture_url = str(request.cookies.get('picture_url', ''))

    if 'report' == body.lower():
        # reset report variables/cookies
        vehicle_id = ''
        agency_name = ''
        license_plate = ''
        duration = 0
        description = ''
        location = ''
        picture_url = ''

        step = handle_start_report(step, twiml)

    elif step == 1:
        location, step = handle_location_step(body, step, twiml)

    elif step == 2:
        agency_name, step = handle_agency_step(body, step, twiml)

    elif step == 3:
        agency_name, step = handle_other_agency_step(body, step, twiml)

    elif step == 4:
        license_plate, step = handle_license_plate_step(body, step, twiml)

    elif step == 5:
        vehicle_id, step = handle_vehicle_id_step(body, step, twiml)

    elif step == 6:
        duration, step = handle_duration_step(body, step, twiml)

    elif step == 7:
        description, step = handle_description_step(body, step, twiml)

    elif step == 8:
        picture_url, step, image_job_id = handle_picture_step(
            body, step, message_sid, twilio_hosted_media_url, twiml)

        new_incident = handle_create_report(agency_name, description, duration,
                                            license_plate, location,
                                            picture_url, vehicle_id)

        start_attach_job(image_job_id, new_incident)

        # reset report variables/cookies
        step = 0

    else:
        twiml.message('Welcome to {}! Please reply "report" to report an '
                      'idling incident.'
                      .format(current_app.config['APP_NAME']))

    response = make_response(str(twiml))

    set_cookie(response, 'messagecount', str(step))
    set_cookie(response, 'agency_name', agency_name)
    set_cookie(response, 'vehicle_id', vehicle_id)
    set_cookie(response, 'license_plate', license_plate)
    set_cookie(response, 'duration', str(duration))
    set_cookie(response, 'description', description)
    set_cookie(response, 'location', location)
    set_cookie(response, 'picture_url', picture_url)

    return response


def start_attach_job(image_job_id, new_incident):
    if image_job_id is not None:
        get_queue().enqueue(
            attach_image_to_incident_report,
            depends_on=image_job_id,
            incident_report=new_incident,
            image_job_id=image_job_id,
        )


def handle_create_report(agency_name, description, duration, license_plate,
                         location, picture_url, vehicle_id):
    lat, lon = geocode(location)
    agency = Agency.get_agency_by_name(agency_name)
    if agency is None:
        agency = Agency(name=agency_name, is_official=False,
                        is_public=True)
        db.session.add(agency)
        db.session.commit()
    new_incident = IncidentReport(
        agency=agency,
        vehicle_id=vehicle_id,
        license_plate=license_plate if license_plate else None,
        duration=timedelta(minutes=duration),
        description=description,
        location=Location(
            latitude=lat,
            longitude=lon,
            original_user_text=location
        ),
        picture_url=picture_url if picture_url else None
    )
    db.session.add(new_incident)
    db.session.commit()
    return new_incident


def get_request_values():
    body = str(request.values.get('Body')).lower().strip()
    num_media = int(request.values.get('NumMedia'))
    twilio_hosted_media_url = str(request.values.get('MediaUrl0')) \
        if num_media > 0 else None
    message_sid = str(request.values.get('MessageSid'))
    return body, message_sid, twilio_hosted_media_url


def handle_start_report(step, twiml):
    step = 1
    twiml.message('What is your location? Be specific! (e.g. "34th and '
                  'Spruce in Philadelphia PA")')
    return step


def handle_location_step(body, step, twiml):
    validator_form = IncidentReportForm()
    errors = data_errors(form=validator_form, field=validator_form.location,
                         data=body)

    if geocode(body) == (None, None):
        errors.append('We could not find that location. Please respond with a '
                      'full address including city and state.')
    if len(errors) == 0:
        location = body
        step += 1
        agencies = Agency.query.filter_by(is_official=True).order_by(
            Agency.name).all()
        letters = all_strings(len(agencies) + 1)  # one extra letter for Other
        agencies_listed = get_agencies_listed(agencies, letters)
        twiml.message('Which agency operates the vehicle you see idling? '
                      'Select from the following list or enter {} for Other.'
                      .format(letters[-1]))
        twiml.message(agencies_listed)
    else:
        location = ''
        reply_with_errors(errors, twiml, 'location')

    return location, step


def handle_agency_step(body_upper, step, twiml):
    body_upper = body_upper.upper()
    agencies = Agency.query.filter_by(is_official=True).all()
    letters = all_strings(len(agencies) + 1)  # one extra letter for Other
    letters_to_agency = dict(zip(letters, agencies))

    if body_upper == letters[-1]:  # Other
        step += 1
        agency_name = ''
        twiml.message('You selected Other. What is the name of the agency '
                      'which operates the vehicle?')

    elif body_upper in letters_to_agency.keys():
        step += 2
        agency_name = letters_to_agency[body_upper].name
        twiml.message('What is the license plate number? Reply "no" to skip. '
                      '(e.g. MG1234E)')

    else:
        agency_name = ''
        twiml.message('Please enter a letter A through {}.'
                      .format(letters[-1]))

    return agency_name, step


def handle_other_agency_step(body, step, twiml):
    agency_name = body
    step += 1
    twiml.message('What is the license plate number? Reply "no" to skip. '
                  '(e.g. MG1234E)')

    return agency_name, step


def handle_license_plate_step(body, step, twiml):
    if body.lower() == 'no':
        body = ''

    validator_form = IncidentReportForm()
    errors = data_errors(
        form=validator_form,
        field=validator_form.license_plate,
        data=body
    )
    if len(errors) == 0:
        license_plate = body
        step += 1
        twiml.message('What is the Vehicle ID? This is usually on the back or '
                      'side of the vehicle. (e.g. 105014)')
    else:
        license_plate = ''
        reply_with_errors(errors, twiml, 'license plate')

    return license_plate, step


def handle_vehicle_id_step(body, step, twiml):
    validator_form = IncidentReportForm()
    errors = data_errors(form=validator_form, field=validator_form.vehicle_id,
                         data=body)

    if len(errors) == 0:
        vehicle_id = body
        step += 1
        twiml.message('How many minutes have you observed the vehicle idling? '
                      '(eg. 10)')
    else:
        vehicle_id = ''
        reply_with_errors(errors, twiml, 'vehicle ID')

    return vehicle_id, step


def handle_duration_step(body, step, twiml):
    errors = []
    try:
        body = int(body)
    except ValueError:
        errors.append('Please enter a valid integer.')

    if len(errors) == 0:
        duration = body
        step += 1
        twiml.message('Please describe the situation (eg. The driver is '
                      'sleeping)')
    else:
        duration = 0
        reply_with_errors(errors, twiml, 'duration')

    return duration, step


def handle_description_step(body, step, twiml):
    validator_form = IncidentReportForm()
    errors = data_errors(form=validator_form, field=validator_form.description,
                         data=body)

    if len(errors) == 0:
        description = body
        step += 1
        twiml.message('Last, can you take a photo of the vehicle and text '
                      'it back? Reply "no" to skip.')
    else:
        description = ''
        reply_with_errors(errors, twiml, 'description')

    return description, step


def handle_picture_step(body, step, message_sid, twilio_hosted_media_url,
                        twiml):
    image_job_id = None
    if twilio_hosted_media_url is not None:
        account_sid = current_app.config['TWILIO_ACCOUNT_SID']
        auth_token = current_app.config['TWILIO_AUTH_TOKEN']

        image_job_id = get_queue().enqueue(
            upload_image,
            imgur_client_id=current_app.config['IMGUR_CLIENT_ID'],
            imgur_client_secret=current_app.config['IMGUR_CLIENT_SECRET'],
            app_name=current_app.config['APP_NAME'],
            image_url=twilio_hosted_media_url
        ).id

        get_rq_scheduler().enqueue_in(
            timedelta(minutes=10),
            delete_mms,
            account_sid=account_sid,
            auth_token=auth_token,
            message_sid=message_sid
        )
    twiml.message('Thanks! See your report at {}'
                  .format(url_for('main.index')))

    return '', step, image_job_id


def reply_with_errors(errors, twiml, field_name):
    twiml.message('Sorry, there were some errors with your response. '
                  'Please enter the {} again.'.format(field_name))
    twiml.message('Errors:\n{}'.format('\n'.join(errors)))


def delete_mms(account_sid, auth_token, message_sid):
    client = TwilioRestClient(account_sid, auth_token)
    for media in client.messages.get(message_sid).media_list.list():
        media.delete()


def attach_image_to_incident_report(incident_report, image_job_id):
    link, deletehash = get_queue().fetch_job(image_job_id).result
    incident_report.picture_url = link
    incident_report.deletehash = deletehash
    db.session.add(incident_report)
    db.session.commit()


def get_agencies_listed(agencies, letters):
    agencies_listed = '\n'.join(
        '{}: {}'.format(l, ag.name) for l, ag in zip(letters, agencies)
    )
    agencies_listed += '\n{}: Other'.format(letters[-1])
    return agencies_listed


def all_strings(max_count):
    """Makes a alphabetical list from a to z and then continues with
    letter combinations. Modified from
    http://stackoverflow.com/questions/29351492/how-to-make-a-continuous-alphabetic-list-python-from-a-z-then-from-aa-ab-ac-e"""  # noqa
    repeat_size = 1
    count = 0
    ret = []
    while True:
        for s in itertools.product(string.ascii_uppercase, repeat=repeat_size):
            count += 1
            if count > max_count:
                return ret
            ret.append(''.join(s))
        repeat_size += 1


def reset_cookies(resp):
    resp.set_cookie('messagecount', expires=0)
    resp.set_cookie('agency_name', expires=0)
    resp.set_cookie('vehicle_id', expires=0)
    resp.set_cookie('license_plate', expires=0)
    resp.set_cookie('duration', expires=0)
    resp.set_cookie('description', expires=0)
    resp.set_cookie('location', expires=0)


def set_cookie(resp, key, val):
    expires = datetime.utcnow() + timedelta(hours=1)
    expires_str = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
    resp.set_cookie(key, value=val, expires=expires_str)


def data_errors(field, data, form):
    """TODO: docstring"""
    field.data = data
    field.raw_data = data
    validated = field.validate(form)

    if not validated:
        return field.errors

    return []
