from wtforms import ValidationError
from models import User


class UniqueEmail(object):
    """Check the database to ensure that the email is unique"""

    def __call__(self, form, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class UniquePhoneNumber(object):
    """Check the database to ensure that the phone number is unique"""

    def __call__(self, form, field):
        if User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('Phone number already registered.')
