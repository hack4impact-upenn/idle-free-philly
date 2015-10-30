from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, Optional
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
