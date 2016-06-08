from wtforms import ValidationError
from wtforms.validators import Required, Optional
from app.models import User, Agency
from app.utils import parse_phone_number, strip_non_alphanumeric_chars, geocode


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


class UniqueAgencyName(object):
    """Check the database to ensure that the agency name is unique"""

    def __call__(self, form, field):
        if Agency.query.filter_by(name=field.data.upper()).first():
            raise ValidationError('An agency with the name "{}" already '
                                  'exists. You can edit that agency on the '
                                  'Manage Agencies page.'
                                  .format(field.data.upper()))


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
        self.message = message

        if self.message is None:
            self.message = 'String was not correctly formatted. After ' \
                           'removing all non-alphanumeric characters, the ' \
                           'length of the string must be between {} and {} ' \
                           'characters.'.format(self.min_length,
                                                self.max_length)

    def __call__(self, form, field):
        stripped = strip_non_alphanumeric_chars(field.data)
        if not (self.min_length <= len(stripped) <= self.max_length):
            raise ValidationError(self.message)


class ValidLocation(object):
    """Geocode the address to make sure it is valid."""
    def __call__(self, form, field):
        lat, lng = geocode(field.data)
        if lat is None or lng is None:
            raise ValidationError('We could not find that location. Please '
                                  'respond with a full address including city '
                                  'and state.')


class RequiredIf(object):
    """Copied from https://gist.github.com/devxoul/7638142


    Validates field conditionally.
    Usage::
        login_method = StringField('', [AnyOf(['email', 'facebook'])])
        email = StringField('', [RequiredIf(login_method='email')])
        password = StringField('', [RequiredIf(login_method='email')])
        facebook_token = StringField('', [RequiredIf(login_method='facebook')])
    """
    def __init__(self, *args, **kwargs):
        self.conditions = kwargs

    def __call__(self, form, field):
        for name, data in self.conditions.iteritems():
            if name not in form._fields:
                Optional(form, field)
            else:
                condition_field = form._fields.get(name)
                if condition_field.data == data and not field.data:
                    Required()(form, field)
        Optional()(form, field)
