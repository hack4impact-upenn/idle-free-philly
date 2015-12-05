from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField
# from wtforms.fields.html5 import EmailField, TelField
# from wtforms.ext.sqlalchemy.fields import QuerySelectField
# from wtforms.validators import Length, Email, Optional, InputRequired
# from ..custom_validators import (...)
# TODO validate form
# from ..models import Role
# from .. import db


class ChangeReportInfoForm(Form):
    # TODO set fields and validators
    vehicle_id = StringField('Vehicle ID')
    submit = SubmitField('Update report')
