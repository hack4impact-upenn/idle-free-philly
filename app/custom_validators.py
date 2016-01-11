from wtforms import ValidationError
from app.models import User
from app.utils import parse_phone_number, strip_non_alphanumeric_chars


class UniqueEmail(object):
    """Check the database to ensure that the email is unique"""

    def __call__(self, form, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class UniquePhoneNumber(object):
    """Check the database to ensure that the phone number is unique"""

    def __call__(self, form, field):
        stripped_number = parse_phone_number(field.data)
        if User.query.filter_by(phone_number=stripped_number).first():
            raise ValidationError('Phone number already registered.')


class PhoneNumberLength(object):
    """Phone number should be number of length min_length to max_length after
    removing non-digit characters."""

    def __init__(self, min_length=0, max_length=15):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, form, field):
        stripped_number = parse_phone_number(field.data)
        if not (self.min_length <= len(stripped_number) <= self.max_length):
            raise ValidationError('Phone number was not correctly formatted. '
                                  'Enter something like \"123 456 7898\"')


class StrippedLength(object):
    """String should be number of length min_length to max_length after
    removing non-alphanumeric characters."""

    def __init__(self, min_length=0, max_length=15, message=None):
        self.min_length = min_length
        self.max_length = max_length

        if message is None:
            self.message = 'String was not correctly formatted. After ' \
                           'stripping all non-alphanumeric characters, the ' \
                           'length of the string must be between {} and {} ' \
                           'characters.'.format(self.min_length,
                                                self.max_length)

    def __call__(self, form, field):
        stripped = strip_non_alphanumeric_chars(field.data)
        if not (self.min_length <= len(stripped) <= self.max_length):
            raise ValidationError(self.message)
