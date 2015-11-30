from flask import render_template
from . import main
from app.models import IncidentReport


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/map')
def get_map():
    """Get information on all Incident Reports in the db, and
    pass to map.html
    """
    return render_template('main/map.html',
                           incident_reports=IncidentReport.query.all())
