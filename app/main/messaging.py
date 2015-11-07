from flask import request, session
from . import main
import twilio.twiml


@main.route("/report_incident", methods=['GET', 'POST'])
def handle_message():
    step = session.get('step', 0)

    message = request.values.get('Body')  # noqa
    resp = twilio.twiml.Response()

    if step is 0:
        resp.message("Welcome to step 0")
    elif step is 1:
        resp.message("Welcome to step 1")
    elif step is 2:
        resp.message("Welcome to step 2")
    else:
        resp.message("Welcome to the final step")

    session['step'] = step + 1
    return str(resp)
