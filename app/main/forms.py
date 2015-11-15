from flask.ext.wtf import Form
from wtforms.fields import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, HiddenField, \
                                        BooleanField, FileField, FloatField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from ..custom_validators import (
    UniqueEmail,
    UniquePhoneNumber,
    PhoneNumberLength,
)
from ..models import Role
from .. import db

class NewIncidentForm(Form):
    license_plate_number = StringField('Vehicle ID')
    vehicle_ID = StringField('License Plate Number')
    notes = StringField('Notes')
    latitude = FloatField('latitude')
    location = StringField('location')
    longitude = FloatField('longitude')
    current_longitude = HiddenField('current_longitude')
    current_latitude = HiddenField('current_latitude')
    use_current_location = BooleanField('Use Current Location')
    idling_duration = IntegerField('Idling Duration')
    submit = SubmitField('Create Report')

