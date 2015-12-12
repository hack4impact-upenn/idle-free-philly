import datetime as datetime

from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField, IntegerField, \
    TextAreaField, HiddenField, DateField, FileField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import (
    InputRequired,
    Regexp,
    Length,
    Optional,
    NumberRange
)

from ..models import Agency
from .. import db


class NewIncidentForm(Form):
    vehicle_ID = IntegerField('Vehicle ID', validators=[
        InputRequired('Vehicle ID is required.'),
        Length(min=2, max=10)
    ])

    license_plate_number = StringField('License Plate Number', validators=[
        InputRequired('License plate is required.'),
        Regexp("^[a-zA-Z0-9]*$",
               message='License plate number must '
                       'consist of only letters and numbers.'),
        Length(min=6, max=7)
    ])

    bus_number = IntegerField('Bus Number', validators=[
        Optional()
    ])

    led_screen_number = IntegerField('LED Screen Number', validators=[
        Optional()
    ])

    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')
    location = StringField('Address')

    date = DateField('Date', default=datetime.date.today(),
                     validators=[InputRequired()])

    duration = IntegerField('Idling Duration (in minutes)', [
        InputRequired('Idling duration (in minutes) is required.'),
        NumberRange(min=0,
                    max=10000,
                    message='Idling duration must be between'
                            '0 and 10000 minutes.')
    ])

    agency = QuerySelectField('Vehicle Agency ',
                              validators=[InputRequired()],
                              get_label='name',
                              query_factory=lambda: db.session.query(Agency))

    picture = FileField('Upload a picture of the vehicle and/or driver.',
                        validators=[Optional()])

    notes = TextAreaField('Additional Notes', [
        Optional(),
        Length(max=5000)
    ])

    submit = SubmitField('Create Report')
