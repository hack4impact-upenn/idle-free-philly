from flask.ext.wtf import Form
from wtforms.fields import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
)
from wtforms.fields.html5 import EmailField, TelField
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    Optional,
    ValidationError,
)
from ..custom_validators import (
    UniqueEmail,
    UniquePhoneNumber,
    PhoneNumberLength,
)
from ..models import User


class LoginForm(Form):
    email = EmailField('Email', validators=[
        DataRequired(),
        Length(1, 64),
        Email()
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(Form):
    first_name = StringField('First name', validators=[
        DataRequired(),
        Length(1, 64)
    ])
    last_name = StringField('Last name', validators=[
        DataRequired(),
        Length(1, 64)
    ])
    email = EmailField('Email', validators=[
        DataRequired(),
        Length(1, 64),
        Email(),
        UniqueEmail(),
    ])
    phone_number = TelField('Phone Number', validators=[
        Optional(),
        PhoneNumberLength(1, 15),
        UniquePhoneNumber(),
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('password2', 'Passwords must match')
    ])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')


class RequestResetPasswordForm(Form):
    email = EmailField('Email', validators=[
        DataRequired(),
        Length(1, 64),
        Email()])
    submit = SubmitField('Reset password')

    # We don't validate the email address so we don't confirm to attackers
    # that an account with the given email exists.


class ResetPasswordForm(Form):
    email = EmailField('Email', validators=[
        DataRequired(),
        Length(1, 64),
        Email(),
    ])
    new_password = PasswordField('New password', validators=[
        DataRequired(),
        EqualTo('new_password2', 'Passwords must match.')
    ])
    new_password2 = PasswordField('Confirm new password',
                                  validators=[DataRequired()])
    submit = SubmitField('Reset password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class CreatePasswordForm(Form):
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('password2', 'Passwords must match.')
    ])
    password2 = PasswordField('Confirm new password',
                              validators=[DataRequired()])
    submit = SubmitField('Set password')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[
        DataRequired(),
        EqualTo('new_password2', 'Passwords must match.')
    ])
    new_password2 = PasswordField('Confirm new password',
                                  validators=[DataRequired()])
    submit = SubmitField('Update password')


class ChangeEmailForm(Form):
    email = EmailField('New email', validators=[
        DataRequired(),
        Length(1, 64),
        Email(),
        UniqueEmail(),
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update email')


class ChangePhoneNumberForm(Form):
    phone_number = TelField('New phone number', validators=[
        DataRequired(),
        PhoneNumberLength(1, 15),
        UniquePhoneNumber(),
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update phone number')
