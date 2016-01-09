from flask import render_template
from flask.ext.login import current_user
from ..models import EditableHTML, IncidentReport
from . import main


@main.route('/')
@main.route('/map')
def index():
    """Get information on all Incident Reports in the db, and
    pass to map.html
    """
    return render_template('main/map.html', current_user=current_user,
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
