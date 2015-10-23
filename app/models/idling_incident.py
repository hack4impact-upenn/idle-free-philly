from .. import db


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))
    original_user_text = db.Column(db.Text)  # the raw text which we geocoded
    idling_incident_id = db.Column(db.Integer,
                                   db.ForeignKey('idling_incidents.id'))


class IdlingIncident(db.Model):
    __tablename__ = 'idling_incidents'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(8))
    license_plate = db.Column(db.String(8))
    location = db.relationship('Location',
                               uselist=False,
                               lazy='joined',
                               backref='idling_incident')
    date = db.Column(db.DateTime)  # hour the incident occurred
    duration = db.Column(db.Interval)  # like timedelta object
    # agency = TODO: Hook this up with agency when Nancy finishes. TODO: set
    # default=<Other> for this field
    picture_url = db.Column(db.Text)
    description = db.Column(db.Text)
