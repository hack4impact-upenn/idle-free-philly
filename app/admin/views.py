from ..decorators import admin_required

from flask import render_template, abort, redirect, flash, url_for, request, Response, make_response
from flask.ext.login import login_required, current_user

from forms import (
    ChangeUserEmailForm,
    ChangeUserPhoneNumberForm,
    ChangeAccountTypeForm,
    InviteUserForm,
    ChangeAgencyOfficialStatusForm,
    ChangeAgencyPublicStatusForm,
)
from . import admin
from ..models import User, Role, Agency, EditableHTML, IncidentReport
from .. import db
from ..utils import parse_phone_number
from ..email import send_email
import csv, StringIO


@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(role=form.role.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    phone_number=parse_phone_number(form.phone_number.data))
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email,
                   'You Are Invited To Join',
                   'account/email/invite',
                   user=user,
                   user_id=user.id,
                   token=token)
        flash('User {} successfully invited'.format(user.full_name()),
              'form-success')
    return render_template('admin/invite_user.html', form=form)


@admin.route('/users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    agencies = Agency.query.all()
    return render_template('admin/registered_users.html', users=users,
                           roles=roles, agencies=agencies)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Email for user {} successfully changed to {}.'
              .format(user.full_name(), user.email),
              'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/change-phone-number',
             methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_phone_number(user_id):
    """Change a user's phone number."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserPhoneNumberForm()
    if form.validate_on_submit():
        user.phone_number = parse_phone_number(form.phone_number.data)
        db.session.add(user)
        db.session.commit()
        flash('Phone number for user {} successfully changed to {}.'
              .format(user.full_name(), user.phone_number),
              'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/change-account-type',
             methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Role for user {} successfully changed to {}.'
              .format(user.full_name(), user.role.name),
              'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/agencies')
@login_required
@admin_required
def all_agencies():
    """View all agencies."""
    agencies = Agency.query.all()
    return render_template('admin/all_agencies.html', agencies=agencies)


@admin.route('/agency/<int:agency_id>')
@admin.route('/agency/<int:agency_id>/info')
@login_required
@admin_required
def agency_info(agency_id):
    """View an agency's information."""
    agency = Agency.query.filter_by(id=agency_id).first()
    if agency is None:
        abort(404)
    return render_template('admin/manage_agency.html', agency=agency)


@admin.route('/agency/<int:agency_id>/change-official-status',
             methods=['GET', 'POST'])
@login_required
@admin_required
def change_agency_official_status(agency_id):
    """Make an agency official or unofficial."""
    agency = Agency.query.filter_by(id=agency_id).first()
    if agency is None:
        abort(404)
    form = ChangeAgencyOfficialStatusForm()
    if form.validate_on_submit():
        agency.is_official = (form.is_official.data == 'y')
        db.session.add(agency)
        db.session.commit()
        flash('Official status for agency {} successfully changed.'
              .format(agency.name),
              'form-success')
    form.is_official.default = 'y' if agency.is_official else 'n'
    form.process()
    return render_template('admin/manage_agency.html', agency=agency,
                           form=form)


@admin.route('/agency/<int:agency_id>/change-public-status',
             methods=['GET', 'POST'])
@login_required
@admin_required
def change_agency_public_status(agency_id):
    """Make an agency official or unofficial."""
    agency = Agency.query.filter_by(id=agency_id).first()
    if agency is None:
        abort(404)
    form = ChangeAgencyPublicStatusForm()
    if form.validate_on_submit():
        agency.is_public = (form.is_public.data == 'y')
        db.session.add(agency)
        db.session.commit()
        flash('Public status for agency {} successfully changed.'
              .format(agency.name),
              'form-success')
    form.is_public.default = 'y' if agency.is_public else 'n'
    form.process()
    return render_template('admin/manage_agency.html', agency=agency,
                           form=form)


@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.get_editable_html(editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200


@admin.route('/get_reports', methods=['GET'])
@login_required
@admin_required
def get_reports():
    '''outfile = open('dump.csv', 'wb')
    outcsv = csv.writer(outfile)
    incident_reports = IncidentReport.query.all()
    outcsv.writerows(incident_reports)
    outfile.close()'''

    outfile = open('mydump.csv', 'w+')
    print('initial file contents:', outfile.read())

    wr = csv.writer(outfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    reports = db.session.query(IncidentReport).all()
    wr.writerow(['VEHICLE ID', 'LICENSE PLATE', 'LOCATION', 'DATE', 'DURATION', 'AGENCY ID', 'DESCRIPTION'])
    for r in reports:
        print('vehicle id:', r.vehicle_id)
        wr.writerow([r.date, r.location, r.agency_id, r.vehicle_id,
                     r.duration,
                     r.license_plate,
                     r.description])

    endfile = open('mydump.csv', 'r+')
    data = endfile.read()
    return Response(
        data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=mydump.csv"})
