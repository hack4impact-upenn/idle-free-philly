from flask import request, session
from . import main
import twilio.twiml


@main.route("/report_incident", methods=['GET', 'POST'])
def handle_message():
    message = str(request.values.get('Body'))  # noqa
    resp = twilio.twiml.Response()
    if "report" in message.lower():
        step = session.get('step', 0)
        if step is 0:
            resp.message("Which Agency Owns the Vehicle? A)SEPTA Bus, B)SEPTA CCT, C)SEPTA, D)PWD, E)PECO, F)Streets, G)Others")  # noqa
        elif step is 1:
            resp.message("What is the License Plate Number? (eg.MG-1234E)")
        elif step is 2:
            resp.message("What is the Vehicle ID? (eg.105014)")
        elif step is 3:
            resp.message("How many minutes has it been Idling for? (eg. 10)")
        elif step is 4:
            resp.message("Please describe the situation (eg. The driver is sleeping)")  # noqa
        else:
            resp.message("Thanks!")
        session['step'] = step + 1
    return str(resp)
main.secret_key = '7c\xf9\r\xa7\xea\xdc\xef\x96\xf7\x8c\xaf\xdeW!\x81jp\xf7[}%\xda2'  # noqa
