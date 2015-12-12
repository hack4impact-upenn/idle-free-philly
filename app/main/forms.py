from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField, IntegerField, TextAreaField, HiddenField, \
    FloatField, DateField, FileField
from wtforms import validators
from ..models import Agency
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from .. import db
import datetime as datetime


class NewIncidentForm(Form):
    license_plate_number = StringField('License Plate Number', [
        validators.required('license plate is required'),
        validators.Regexp('^\w+$',
                          message='license plate number must '
                                  'consist of only letters and numbers!'),
        validators.Length(min=6, max=7)
    ])
    agency = QuerySelectField('Truck Agency ',
                              validators=[DataRequired()],
                              get_label='name',
                              query_factory=lambda: db.session.query(Agency))
    bus_number = IntegerField('Bus Number', [
        validators.optional(),
        validators.NumberRange(min=0,
                               max=100000000,
                               message='invalid bus number entered!')
    ])
    led_screen_number = IntegerField('LED Screen Number', [
        validators.optional(),
        validators.NumberRange(min=0,
                               max=100000000,
                               message='invalid LED Screen Number entered!')
    ])


    vehicle_ID = StringField('Vehicle ID', [
        validators.required('vehicleID is required'),
        validators.Regexp('^[0-9]*$',
                          message='vehicle id must consist of only digits!'),
        validators.Length(min=2, max=10)
    ])
    notes = TextAreaField('Notes', [
        validators.optional(),
        validators.Length(max=100)
    ])
    latitude = HiddenField()
    date = DateField('date', default=datetime.date.today(),
                     validators=[validators.DataRequired()])
    location = StringField('Location')
    longitude = HiddenField('longitude')
    idling_duration = IntegerField('Idling Duration (in minutes)', [
        validators.required('idling duration (in minutes) is required!'),
        validators.NumberRange(min=0,
                               max=1000,
                               message='invalid duration entered!')
    ])
    picture = FileField('Upload a picture of the truck/driver',
                        validators=[validators.optional()])
    submit = SubmitField('Create Report')
