from flask import request, make_response
from . import main
from .. import db
from ..models import Agency, IncidentReport, Location
from datetime import datetime, timedelta
import twilio.twiml


@main.route("/report_incident", methods=['GET', 'POST'])
def handle_message():
    message = str(request.values.get('Body'))
    twiml = twilio.twiml.Response()

    # Retrieve incident cookies
    step = int(request.cookies.get('messagecount', 0))
    vehicle_id = int(request.cookies.get('vehicle_id', 0))
    agency_name = str(request.cookies.get('agency_name', ""))
    license_plate = str(request.cookies.get('license_plate', ""))
    duration = int(request.cookies.get('duration', 0))
    description = str(request.cookies.get('description'))
    location = str(request.cookies.get('location', ""))
    body = str(request.values.get('Body'))
    if step == 0 and "report" in message.lower():
        twiml.message("What is your location?")
    elif step == 1:
        location = body
        twiml.message("""Which Agency Owns the Vehicle? A)SEPTA Bus, B)SEPTA CCT, C)SEPTA, D)PWD, E)PECO, F)Streets, G)Others""")  # noqa
    elif step == 2:
        twiml.message("What is the License Plate Number? (eg.MG-1234E)")
        agency_name = agency_letter_to_name(body)
    elif step == 3:
        twiml.message("What is the Vehicle ID? (eg.105014)")
        license_plate = body
    elif step == 4:
        twiml.message("How many minutes has it been idling for? (eg. 10)")
        vehicle_id = int(body)
    elif step == 5:
        twiml.message("Please describe the situation (eg. The driver is sleeping)")  # noqa
        duration = int(body)
    elif step == 6:
        description = body
        twiml.message("Thanks!")
        agency = Agency.query.filter_by(name=agency_name).first()
        new_incident = IncidentReport(
            agency=agency,
            vehicle_id=vehicle_id,
            license_plate=license_plate,
            duration=timedelta(minutes=duration),
            description=description,
            location=Location(
                original_user_text=location
            )
        )
        db.session.add(new_incident)
        db.session.commit()
        step = -1
    step += 1
    response = make_response(str(twiml))

    # Set cookies
    if step == 0:
        reset_cookies(response)
    else:
        set_cookie(response, 'messagecount', str(step))
        set_cookie(response, 'agency_name', agency_name)
        set_cookie(response, 'vehicle_id', str(vehicle_id))
        set_cookie(response, 'license_plate', license_plate)
        set_cookie(response, 'duration', str(duration))
        set_cookie(response, 'description', description)
        set_cookie(response, 'location', location)
    return response


def reset_cookies(resp):
    resp.set_cookie('messagecount', expires=0)
    resp.set_cookie('agency_name', expires=0)
    resp.set_cookie('vehicle_id', expires=0)
    resp.set_cookie('license_plate', expires=0)
    resp.set_cookie('duration', expires=0)
    resp.set_cookie('description', expires=0)
    resp.set_cookie('location', expires=0)


def set_cookie(resp, key, val):
    expires = datetime.utcnow() + timedelta(hours=4)
    expires_str = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
    resp.set_cookie(key, value=val, expires=expires_str)


def agency_letter_to_name(letter):
    if letter == 'A':
        return "SEPTA BUS"
    elif letter == 'B':
        return "SEPTA CCT"
    elif letter == 'C':
        return "SEPTA"
    elif letter == 'D':
        return "PWD"
    elif letter == 'E':
        return "PECO"
    else:
        return "STREETS"
