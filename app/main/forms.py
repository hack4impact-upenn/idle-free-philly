from flask.ext.wtf import Form
from wtforms.fields import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, HiddenField, \
                                        BooleanField, FileField, FloatField, DateField
from wtforms import validators
from ..models import Agency
from werkzeug.datastructures import MultiDict
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
import datetime as datetime
class NewIncidentForm(Form):
    license_plate_number = StringField('License Plate Number', [
        validators.required('license plate is required'),
        validators.Regexp('^\w+$', message ='license plate number must consist of only letters and numbers!'),
        validators.Length(min = 6, max = 7)
    ])
    agency = QuerySelectField('Truck Agency ', validators=[DataRequired()], get_label='name',
                              query_factory=lambda: db.session.query(Agency))
    vehicle_ID = StringField('Vehicle ID', [
        validators.required('vehicleID is required'),
        validators.Regexp('^[0-9]*$', message='vehicle id must consist of only digits!'),
        validators.Length(min = 2, max = 10)
    ])
    notes = StringField('Notes', [
        validators.optional(),
        validators.Length(max = 100)
    ])
    latitude = FloatField('latitude')
    date = DateField('date', default=datetime.date.today(), validators=[validators.DataRequired()])
    location = StringField('Location')
    longitude = FloatField('longitude')
    idling_duration = IntegerField('Idling Duration (in minutes)', [
        validators.required('idling duration (in minutes) is required!'),
        validators.NumberRange(min = 0, max = 1000, message='invalid duration range!')
    ])
    submit = SubmitField('Create Report')



