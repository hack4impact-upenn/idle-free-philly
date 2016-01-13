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
    body = str(request.values.get('Body'))
    num_media = int(request.values.get('NumMedia'))
    twilio_hosted_media_url = str(request.values.get('MediaUrl0')) \
        if num_media > 0 else None
    message_sid = str(request.values.get('MessageSid'))

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

    print locals()  # TODO: for debugging

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
        step = 1

    elif step == 1:
        location, step = handle_location_step(body, step, twiml)

    elif step == 2:
        agency_name, step = handle_agency_step(body, step, twiml)

    elif step == 3:
        license_plate, step = handle_license_plate_step(body, step, twiml)

    elif step == 4:
        vehicle_id, step = handle_vehicle_id_step(body, step, twiml)

    elif step == 5:
        duration, step = handle_duration_step(body, step, twiml)

    elif step == 6:
        description, step = handle_description_step(body, step, twiml)

    elif step == 7:
        picture_url, step, image_job_id = handle_picture_step(
            body, step, message_sid, twilio_hosted_media_url, twiml)

        (lat, lon) = geocode(location)
        agency = Agency.query.filter_by(name=agency_name).first()
        # TODO: handle empty strings, set attributes to None
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

        get_queue().enqueue(
            attach_image_to_incident_report,
            depends_on=image_job_id,
            incident_report=new_incident,
            image_job_id=image_job_id,
        )

        # reset report variables/cookies
        step = 0
        vehicle_id = ''
        agency_name = ''
        license_plate = ''
        duration = 0
        description = ''
        location = ''
        picture_url = ''

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

    print str(twiml)
    return response


def handle_start_report(step, twiml):
    step = 1
    twiml.message('What is your location? Be specific! (e.g. "34th and '
                  'Spruce in Philadelphia PA")')
    return step


def handle_location_step(body, step, twiml):
    validator_form = IncidentReportForm()

    errors = data_errors(form=validator_form, field=validator_form.location,
                         data=body)
    print geocode(body)
    if geocode(body) is (None, None):
        errors.append('We could not find that location. Please respond with a '
                      'full address including city and state.')
    if len(errors) == 0:
        location = body
        step += 1
        agencies = Agency.query.filter_by(is_official=True).order_by(
            Agency.name).all()
        letters = all_strings(len(agencies) + 1)  # one extra letter for Other
        agencies_listed = get_agencies_listed(agencies, letters)
        twiml.message('Which agency owns the vehicle you see idling? Select '
                      'from the following list or enter {} for Other.'
                      .format(letters[-1]))
        twiml.message(agencies_listed)
    else:
        location = ''
        twiml.message('Sorry, there were some errors with your response. '
                      'Please enter the location again.')
        twiml.message('Errors:\n{}'.format('\n'.join(errors)))
    return location, step


def handle_agency_step(body, step, twiml):
    # TODO: handle other
    agency_name = ''
    agency = agency_letter_to_agency(body)
    if agency is not None:
        agency_name = agency.name
    step += 1
    twiml.message('What is the license plate number? Reply "no" to skip. '
                  '(e.g. MG1234E)')
    return agency_name, step


def handle_license_plate_step(body, step, twiml):
    license_plate = ''
    if body.lower() != 'no':
        license_plate = body
    step += 1
    twiml.message('What is the Vehicle ID? This is usually on the back or '
                  'side of the vehicle. (e.g. 105014)')
    return license_plate, step


def handle_vehicle_id_step(body, step, twiml):
    vehicle_id = body
    step += 1
    twiml.message('How many minutes have you observed the vehicle idling? '
                  '(eg. 10)')
    return vehicle_id, step


def handle_duration_step(body, step, twiml):
    duration = int(body)
    step += 1
    twiml.message('Please describe the situation (eg. The driver is '
                  'sleeping)')
    return duration, step


def handle_description_step(body, step, twiml):
    description = body
    step += 1
    twiml.message('Last, can you take a photo of the vehicle and text '
                  'it back? Reply "no" to skip.')
    return description, step


def handle_picture_step(body, step, message_sid, twilio_hosted_media_url,
                        twiml):
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


def agency_letter_to_agency(input_letter):
    agencies = Agency.query.filter_by(is_official=True).all()
    letters = all_strings(len(agencies) + 1)  # one extra letter for Other
    letters_to_agency = dict(zip(letters, agencies))
    letters_to_agency[letters[-1]] = None
    return letters_to_agency[input_letter]


def data_errors(field, data, form):
    """TODO: docstring"""
    field.data = data
    field.raw_data = data
    validated = field.validate(form)

    if not validated:
        return field.errors

    return []
