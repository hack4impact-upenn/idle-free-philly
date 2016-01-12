import string
import itertools
from flask import request, make_response, current_app
from . import main
from .. import db
from ..utils import geocode
from ..models import Agency, IncidentReport, Location
from datetime import datetime, timedelta
import twilio.twiml


@main.route('/report_incident', methods=['GET'])
def handle_message():
    message = str(request.values.get('Body'))
    num_media = int(request.values.get('NumMedia'))
    twilio_hosted_media_url = str(request.values.get('MediaUrl')) \
        if num_media > 0 else None

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

    body = str(request.values.get('Body'))

    print locals()  # for debugging

    if 'report' == message.lower():
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
        license_plate, step = handle_license_plate_step(body, step, twiml)

    elif step == 4:
        vehicle_id, step = handle_vehicle_id_step(body, step, twiml)

    elif step == 5:
        duration, step = handle_duration_step(body, step, twiml)

    elif step == 6:
        description, step = handle_description_step(body, step, twiml)

    elif step == 7:
        picture_url, step = handle_picture_step(body, twilio_hosted_media_url,
                                                step, twiml)

        twiml.message('Thanks!')
        (lat, lon) = geocode(location)
        agency = Agency.query.filter_by(name=agency_name).first()
        # TODO: handle empty strings, set attributes to None
        new_incident = IncidentReport(
            agency=agency,
            vehicle_id=vehicle_id,
            license_plate=license_plate,
            duration=timedelta(minutes=duration),
            description=description,
            location=Location(
                latitude=lat,
                longitude=lon,
                original_user_text=location
            ),
            picture_url=picture_url
        )
        db.session.add(new_incident)
        db.session.commit()

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

    # if step < 2:
    #     reset_cookies(response)

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


def handle_picture_step(body, twilio_hosted_media_url, step, twiml):
    print twilio_hosted_media_url
    return '', step


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
