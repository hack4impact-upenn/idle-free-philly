from flask import render_template
from flask.ext.login import login_required, current_user
from . import reports
from ..models import IncidentReport, Agency
from ..decorators import admin_or_agency_required


@reports.route('/all')
@admin_or_agency_required
def view_reports():
    """View all idling incident reports.
    Admins can see all reports.
    Agency workers can see reports for their affiliated agencies.
    General users do not have access to this page."""

    agencies = None

    if current_user.is_admin():
        reports = IncidentReport.query.all()
        agencies = Agency.query.all()

    elif current_user.is_agency_worker():
        reports = []
        for agency in current_user.agencies:
            reports.extend(agency.incident_reports)

    # TODO test using real data
    return render_template('reports/reports.html', reports=reports,
                           agencies=agencies, is_individual=False)


@reports.route('/my-reports')
@login_required
def view_my_reports():
    """View all idling incident reports for this user."""
    reports = current_user.incident_reports
    agencies = None

    return render_template('reports/reports.html', reports=reports,
                           agencies=agencies, is_individual=True)
