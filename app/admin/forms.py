from flask.ext.wtf import Form
from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from wtforms import ValidationError
from ..models import User, Role
from .. import db


class ChangeUserEmailForm(Form):
    email = EmailField('New email', validators=[
        DataRequired(),
        Length(1, 64),
        Email()
    ])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangeUserPhoneNumberForm(Form):
    phone_number = TelField('New phone number', validators=[
        DataRequired(),
        Length(1, 15),
        Regexp(r'^[0-9]+$', message='Please enter just the number with no '
                                    'other symbols (e.g. 1234567898)')
    ])
    submit = SubmitField('Update phone number')

    def validate_phone_number(self, field):
        if User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('Phone number already registered.')


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
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64),
                                            Email()])
    phone_number = TelField('Phone Number', validators=[
        Length(0, 15),
        Regexp(r'^[0-9]*$',
               message='Please enter just the number with no other symbols '
                       '(e.g. 1234567898)')
        ])
    submit = SubmitField('Invite')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_phone_number(self, field):
        if User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('Phone number already registered.')


class NewUserForm(InviteUserForm):
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2',
                                'Passwords must match.')
    ])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])

    submit = SubmitField('Create')
