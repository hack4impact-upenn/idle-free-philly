from flask import render_template
from flask.ext.login import login_required, current_user
from . import reports
from ..models import IncidentReport, Agency


@reports.route('/all')
@login_required
def view_reports():
    """View all idling incident reports."""
    """Different roles have access to different reports.
    An Admin can see all reports.
    An Agency worker can all reports for their agency.
    A general user can see all reports submitted by that user."""

    if current_user.is_admin():
        reports = IncidentReport.query.all()
        agencies = Agency.query.all()

    elif current_user.is_agency_worker():
        agency_id = current_user.get_agency_id()
        agencies = Agency.query.filter_by(id=agency_id)
        reports = IncidentReport.query.filter_by(agency_id=agency_id)

    elif current_user.is_general_user():
        # TODO general user reports
        reports = IncidentReport.query.all()
        agencies = Agency.query.all()

    return render_template('reports/reports.html', reports=reports,
                           agencies=agencies, current_user=current_user)
