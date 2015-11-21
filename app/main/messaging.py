from flask import request, make_response
from . import main
from datetime import datetime, timedelta
import twilio.twiml

SECRET_KEY = '7c\xf9\r\xa7\xea\xdc\xef\x96\xf7\x8c\xaf\xdeW!\x81jp\xf7[}%\xda2'  # noqa


@main.route("/report_incident", methods=['GET', 'POST'])
def handle_message():
    message = str(request.values.get('Body'))  # noqa
    twiml = twilio.twiml.Response()
    print twiml

    step = int(request.cookies.get('messagecount', 0))

    if step is 0 and "report" in message.lower():
        twiml.message("Which Agency Owns the Vehicle? A)SEPTA Bus, B)SEPTA CCT, C)SEPTA, D)PWD, E)PECO, F)Streets, G)Others")  # noqa
    elif step is 1:
        twiml.message("What is the License Plate Number? (eg.MG-1234E)")
    elif step is 2:
        twiml.message("What is the Vehicle ID? (eg.105014)")
    elif step is 3:
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
    return response
