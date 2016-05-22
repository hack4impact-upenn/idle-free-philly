import datetime as datetime

from flask.ext.wtf import Form
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields import (
    StringField,
    SubmitField,
    IntegerField,
    TextAreaField,
    HiddenField,
    DateField,
)
from wtforms_components import TimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import (
    InputRequired,
    Length,
    Optional,
    NumberRange,
    URL,
    Regexp,
)

from app.custom_validators import StrippedLength, ValidLocation, RequiredIf
from ..models import Agency
from .. import db


class IncidentReportForm(Form):
    vehicle_id = StringField('Vehicle ID', validators=[
        InputRequired('Vehicle ID is required.'),
        StrippedLength(
            min_length=1,
            max_length=15,
            message='Vehicle ID must be between 1 to 15 characters after '
                    'removing all non-alphanumeric characters.'
        ),
    ])

    license_plate = StringField('License Plate Number', validators=[
        Optional(),
        StrippedLength(
            min_length=1,
            max_length=12,
            message='License plate must be between 1 to 12 characters after '
                    'removing all non-alphanumeric characters.'
        )
    ])

    bus_number = IntegerField('Bus Number', validators=[
        Optional()
    ])

    led_screen_number = IntegerField('LED Screen Number', validators=[
        Optional()
    ])

    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')
    location = StringField('Address', validators=[
        InputRequired(),
        ValidLocation(),

    ])

    today = datetime.datetime.today()
    date = DateField('Date (year-month-day)',
                     default=today.strftime('%m-%d-%Y'),
                     validators=[InputRequired()])
    time = TimeField('Time (hours:minutes am/pm)',
                     default=today.strftime('%I:%M %p'),
                     validators=[InputRequired()])

    duration = IntegerField('Idling Duration (in minutes)', validators=[
        InputRequired('Idling duration is required.'),
        NumberRange(min=0,
                    message='Idling duration must be positive.')
    ])

    agency = QuerySelectField(
        'Vehicle Agency ',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Agency).filter_by(
            is_official=True).order_by(Agency.name),
        allow_blank=True,
        blank_text='Other',
    )

    other_agency = StringField(
        'Other Agency',
        validators=[RequiredIf(agency=None)]
    )

    picture_file = FileField(
        'Upload a picture of the idling vehicle.',
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp'],
                        'Only images are allowed.')
        ]
    )

    picture_url = StringField('Picture URL', validators=[
        Optional(),
        URL(message='Picture URL must be a valid URL. '
                    'Please upload the image to an image hosting website '
                    'and paste the link here.')
        ])

    description = TextAreaField('Additional Notes', validators=[
        Optional(),
        Length(max=5000)
    ])

    submit = SubmitField('Create Report')


class EditIncidentReportForm(IncidentReportForm):
    duration = StringField('Idling Duration (h:m:s)', validators=[
        InputRequired('Idling duration is required.'),
        Regexp(r'^(\d{1,2}:)(\d{1,2}:)(\d{1,2})$',
               message='Write duration as HH:MM:SS')
    ])

    # All agencies should be options in the EditForm but only official agencies
    # should be an option in the ReportForm
    agency = QuerySelectField(
        'Vehicle Agency ',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Agency),
        allow_blank=True,
        blank_text='Other',
    )

    submit = SubmitField('Update Report')
