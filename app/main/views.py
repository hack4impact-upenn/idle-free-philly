from flask import render_template
from ..models import EditableHTML
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


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('main/about.html',
                           editable_html_obj=editable_html_obj)


@main.route('/faq')
def faq():
    editable_html_obj = EditableHTML.get_editable_html('faq')
    return render_template('main/faq.html',
                           editable_html_obj=editable_html_obj)
