import datetime as datetime

from flask import render_template, abort, flash, redirect, url_for
from flask.ext.login import login_required, current_user

from forms import EditIncidentReportForm

from . import reports
from .. import db
from ..models import IncidentReport, Agency
from ..decorators import admin_or_agency_required, admin_required
from ..utils import (
    flash_errors,
    geocode
)


@reports.route('/all')
@admin_or_agency_required
def view_reports():
    """View all idling incident reports.
    Admins can see all reports.
    Agency workers can see reports for their affiliated agencies.
    General users do not have access to this page."""

    agencies = []

    if current_user.is_admin():
        incident_reports = IncidentReport.query.all()
        agencies = Agency.query.all()

    elif current_user.is_agency_worker():
        incident_reports = []
        agencies = current_user.agencies
        for agency in current_user.agencies:
            incident_reports.extend(agency.incident_reports)

    # TODO test using real data
    return render_template('reports/reports.html', reports=incident_reports,
                           agencies=agencies)


@reports.route('/my-reports')
@login_required
def view_my_reports():
    """View all idling incident reports for this user."""
    incident_reports = current_user.incident_reports
    agencies = []

    return render_template('reports/reports.html', reports=incident_reports,
                           agencies=agencies)


@reports.route('/<int:report_id>')
@reports.route('/<int:report_id>/info')
@login_required
@admin_required
def report_info(report_id):
    """View a report"""
    report = IncidentReport.query.filter_by(id=report_id).first()
    if report is None:
        abort(404)
    return render_template('reports/manage_report.html', report=report,
                           return_to_all=True)  # TODO rename


@reports.route('/<int:report_id>/edit_info', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_report_info(report_id):
    """Change the fields for a report"""
    report = IncidentReport.query.filter_by(id=report_id).first()
    if report is None:
        abort(404)
    form = EditIncidentReportForm()

    if form.validate_on_submit():
        report.vehicle_id = form.vehicle_id.data
        report.license_plate = form.license_plate.data

        # reformat location data - TODO error-checking for bad addresses
        lat, lng = geocode(form.location.data)
        report.location.latitude, report.location.longitude = lat, lng
        report.location.original_user_text = form.location.data

        report.date.date = datetime.date(form.date.data)
        report.date.time = datetime.time(form.time.data)

        # reformat duration data - minutes to time-delta
        report.duration = form.duration.data

        report.agency = form.agency.data

        # TODO upload picture_file
        report.picture_url = form.picture_url.data
        report.description = form.description.data

        db.session.add(report)
        db.session.commit()
        flash('Report information updated.', 'form-success')
    elif form.errors.items():
        flash_errors(form)

    # pre-populate form
    form.vehicle_id.default = report.vehicle_id
    form.license_plate.default = report.license_plate
    form.bus_number.default = report.bus_number
    form.led_screen_number.default = report.led_screen_number
    form.location.default = report.location.original_user_text

    # TODO format string
    print type(report.date)
    form.date.default = report.date
    form.time.default = report.date
    # form.date.default = (report.date).strftime('%m-%d-%Y')
    # form.time.default = report.date.strftime('%I:%M %p')

    form.duration.default = report.duration
    form.agency.default = report.agency
    form.picture_url.default = report.picture_url
    form.description.default = report.description
    form.process()

    return render_template('reports/manage_report.html', report=report,
                           form=form)


@reports.route('/<int:report_id>/delete')
@login_required
@admin_required
def delete_report_request(report_id):
    """Request deletion of a report."""
    report = IncidentReport.query.filter_by(id=report_id).first()
    if report is None:
        abort(404)
    return render_template('reports/manage_report.html', report=report)


@reports.route('/<int:report_id>/_delete')
@login_required
@admin_required
def delete_report(report_id):
    """Delete a report"""

    report = IncidentReport.query.filter_by(id=report_id).first()
    db.session.delete(report)
    db.session.commit()
    flash('Successfully deleted report.', 'success')

    return redirect(url_for('reports.view_reports'))
