from flask import request, make_response
from . import main
from datetime import datetime, timedelta
import twilio.twiml
import json


@main.route("/report_incident", methods=['GET', 'POST'])
def handle_message():
    message = str(request.values.get('Body'))  # noqa
    twiml = twilio.twiml.Response()
    step = int(request.cookies.get('messagecount', 0))
    incident_report = json.loads(request.cookies.get('i_report', "{}"))
    if step is 0 and "report" in message.lower():
        twiml.message("Which Agency Owns the Vehicle? A)SEPTA Bus, B)SEPTA CCT, C)SEPTA, D)PWD, E)PECO, F)Streets, G)Others")  # noqa
    elif step is 1:
        incident_report["agency"] = "SEPTOR"
        twiml.message("What is the License Plate Number? (eg.MG-1234E)")
    elif step is 2:
        incident_report["licensePlate"] = "TRAP"
        twiml.message("What is the Vehicle ID? (eg.105014)")
    elif step is 3:
        incident_report["ID"] = "COOKOO FOR COCOAPUFFS"
        twiml.message("How many minutes has it been Idling for? (eg. 10)")
    elif step is 4:
        twiml.message("Please describe the situation (eg. The driver is sleeping)")  # noqa
    else:
        twiml.message("Thanks!")
        step = -1
    step += 1
    expires = datetime.utcnow() + timedelta(hours=4)
    expires_str = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
    response = make_response(str(twiml))
    response.set_cookie('messagecount', value=str(step), expires=expires_str)
    print(json.dumps(incident_report))
    response.set_cookie('i_report', value=json.dumps(incident_report), expires=expires_str)  # noqa
    return response
