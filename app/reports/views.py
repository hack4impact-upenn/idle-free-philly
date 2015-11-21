from flask import render_template
from flask.ext.login import login_required, current_user
from . import reports
from ..models import IncidentReport, Agency
from ..decorators import admin_or_agency_required


@reports.route('/all')
@admin_or_agency_required
def view_reports():
    """View all idling incident reports.
    Different roles have access to different reports.
    An Admin can see all reports.
    An Agency worker can all reports for their agency.
    A general user can see all reports submitted by that user."""

    agencies = None

    if current_user.is_admin():
        reports = IncidentReport.query.all()
        agencies = Agency.query.all()

    elif current_user.is_agency_worker():
        reports = []
        for agency in current_user.agencies:
            reports.extend(agency.incident_reports)

    elif current_user.is_general_user():
        reports = current_user.incident_reports

    # TODO test using real data
    return render_template('reports/reports.html', reports=reports,
                           agencies=agencies, current_user=current_user)


@reports.route('/my-reports')
@login_required
def view_my_reports():
    pass
