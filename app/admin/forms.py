from flask.ext.wtf import Form
from wtforms.fields import StringField, PasswordField, SubmitField, SelectField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    Optional,
    InputRequired
)
from ..custom_validators import (
    UniqueEmail,
    UniquePhoneNumber,
    PhoneNumberLength,
)
from ..models import Role
from .. import db


class ChangeUserEmailForm(Form):
    email = EmailField('New email', validators=[
        DataRequired(),
        Length(1, 64),
        Email(),
        UniqueEmail(),
    ])
    submit = SubmitField('Update email')


class ChangeUserPhoneNumberForm(Form):
    phone_number = TelField('New phone number', validators=[
        DataRequired(),
        PhoneNumberLength(10, 15),
        UniquePhoneNumber(),
    ])
    submit = SubmitField('Update phone number')


class ChangeAccountTypeForm(Form):
    role = QuerySelectField('New account type',
                            validators=[DataRequired()],
                            get_label='name',
                            query_factory=lambda: db.session.query(Role).
                            order_by('permissions'))
    submit = SubmitField('Update role')


class InviteUserForm(Form):
    role = QuerySelectField('Account type',
                            validators=[DataRequired()],
                            get_label='name',
                            query_factory=lambda: db.session.query(Role).
                            order_by('permissions'))
    first_name = StringField('First name', validators=[DataRequired(),
                                                       Length(1, 64)])
    last_name = StringField('Last name', validators=[DataRequired(),
                                                     Length(1, 64)])
    email = EmailField('Email', validators=[
        DataRequired(),
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


class NewUserForm(InviteUserForm):
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('password2', 'Passwords must match.')
    ])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])

    submit = SubmitField('Create')


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
