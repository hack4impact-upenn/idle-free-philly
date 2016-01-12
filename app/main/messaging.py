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
    twiml = twilio.twiml.Response()

    # Retrieve incident cookies
    step = int(request.cookies.get('messagecount', 0))
    vehicle_id = str(request.cookies.get('vehicle_id', ''))
    agency_name = str(request.cookies.get('agency_name', ''))
    license_plate = str(request.cookies.get('license_plate', ''))
    duration = int(request.cookies.get('duration', 0))
    description = str(request.cookies.get('description', ''))
    location = str(request.cookies.get('location', ''))

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

        step = 1
        twiml.message('What is your location? Be specific! (e.g. "34th and '
                      'Spruce in Philadelphia PA")')

    elif step == 1:
        location = body
        step += 1

        agencies = Agency.query.filter_by(is_official=True).order_by(
            Agency.name).all()
        letters = all_strings(len(agencies) + 1)  # one extra letter for Other
        agencies_listed = '\n'.join(
            '{}:{}'.format(l, ag.name) for l, ag in zip(letters, agencies)
        )
        agencies_listed += '\n{}:Other'.format(letters[-1])

        twiml.message('Which agency owns the vehicle you see idling? Select '
                      'from the following list or enter {} for Other.'
                      .format(letters[-1]))
        twiml.message(agencies_listed)

    elif step == 2:
        # TODO: handle other
        agency = agency_letter_to_agency(body)
        if agency is not None:
            agency_name = agency.name

        step += 1
        twiml.message('What is the license plate number? Reply "no" to skip. '
                      '(e.g. MG1234E)')

    elif step == 3:
        license_plate = body
        step += 1
        twiml.message('What is the Vehicle ID? This is usually on the back or '
                      'side of the vehicle. (e.g. 105014)')

    elif step == 4:
        vehicle_id = str(body)
        step += 1
        twiml.message('How many minutes have you observed the vehicle idling? '
                      '(eg. 10)')

    elif step == 5:
        duration = int(body)
        step += 1
        twiml.message('Please describe the situation (eg. The driver is '
                      'sleeping)')

    # TODO: mms

    elif step == 6:
        description = body
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
            )
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
    print str(twiml)
    return response


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
