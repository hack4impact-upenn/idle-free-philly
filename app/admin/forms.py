from flask.ext.wtf import Form
from wtforms import ValidationError
from wtforms.fields import StringField, SubmitField, SelectField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.ext.sqlalchemy.fields import (
    QuerySelectField,
    QuerySelectMultipleField
)
from wtforms.validators import Length, Email, Optional, InputRequired
from ..custom_validators import (
    UniqueEmail,
    UniquePhoneNumber,
    PhoneNumberLength,
    UniqueAgencyName
)
from ..models import Role, Agency
from .. import db


class ChangeUserEmailForm(Form):
    email = EmailField('New email', validators=[
        InputRequired(),
        Length(1, 64),
        Email(),
        UniqueEmail(),
    ])
    submit = SubmitField('Update email')


class ChangeUserPhoneNumberForm(Form):
    phone_number = TelField('New phone number', validators=[
        InputRequired(),
        PhoneNumberLength(10, 15),
        UniquePhoneNumber(),
    ])
    submit = SubmitField('Update phone number')


class ChangeAccountTypeForm(Form):
    role = QuerySelectField('New account type',
                            validators=[InputRequired()],
                            get_label='name',
                            query_factory=lambda: db.session.query(Role).
                            order_by('permissions'))
    submit = SubmitField('Update role')


class ChangeAgencyAffiliationsForm(Form):
    agency_affiliations = QuerySelectMultipleField(
        'Agency affiliations',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Agency).filter_by(
            is_official=True).order_by('name')
    )
    submit = SubmitField('Update agency affiliations')


class InviteUserForm(Form):
    role = QuerySelectField(
        'Account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions')
    )
    agency_affiliations = QuerySelectMultipleField(
        'Agency affiliations',
        get_label='name',
        query_factory=lambda: db.session.query(Agency).filter_by(
            is_official=True).order_by('name')
    )
    first_name = StringField('First name', validators=[InputRequired(),
                                                       Length(1, 64)])
    last_name = StringField('Last name', validators=[InputRequired(),
                                                     Length(1, 64)])
    email = EmailField('Email', validators=[
        InputRequired(),
        Length(1, 64),
        Email(),
        UniqueEmail()
    ])
    phone_number = TelField('Phone Number', validators=[
        Optional(),
        PhoneNumberLength(10, 15),
        UniquePhoneNumber(),
    ])
    submit = SubmitField('Invite')

    @staticmethod
    def validate_agency_affiliations(form, field):
        if form.role.data.name == 'AgencyWorker' and len(field.data) == 0:
            raise ValidationError('Agency affiliation must be set for workers')


class AddAgencyForm(Form):
    name = StringField(
        'Agency name',
        validators=[
            InputRequired(),
            Length(1, 64),
            UniqueAgencyName(),
        ]
    )
    is_public = SelectField(
        'Publicly visible',
        description='If an agency is set as public, then all new incident '
                    'reports created for that agency will show this agency to '
                    'the general public by default. That is, the marker on '
                    'the map will name this particular agency as the type of '
                    'vehicle which was idling. If an agency is not set as '
                    'public, then all new incident reports created for that '
                    'agency will not show this agency by default. Note: this '
                    'setting will not change anything for reports which were '
                    'created in the past. To change whether the agency is '
                    'displayed for past reports, you must edit that report '
                    'individually on the reports page.',
        # TODO add a link here once we know the route to the reports page
        choices=[('y', 'Yes'), ('n', 'No')],
        validators=[InputRequired()],
    )
    submit = SubmitField('Create agency')


class ChangeAgencyOfficialStatusForm(Form):
    is_official = SelectField(
        'Officially Approved',
        description='Officially approved agencies show up on the reporting '
                    'form in the \"agency\" dropdown and can be linked to '
                    'Agency Workers. Agencies which are not officially '
                    'approved were added by users in the \"other\" option of '
                    'the reporting form.',
        choices=[('y', 'Yes'), ('n', 'No')],
        validators=[InputRequired()],
    )
    submit = SubmitField('Update status')


class ChangeAgencyPublicStatusForm(Form):
    is_public = SelectField(
        'Publicly visible',
        description='The public does not see the agency connected to an '
                    'idling incident if that agency is not publicly visible. '
                    'Agencies which are not publicly visible still have '
                    'anonymized reports which the public can see.',
        choices=[('y', 'Yes'), ('n', 'No')],
        validators=[InputRequired()],
    )
    submit = SubmitField('Update status')
