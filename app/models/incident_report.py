from .. import db
from . import Agency, User


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))
    original_user_text = db.Column(db.Text)  # the raw text which we geocoded
    incident_report_id = db.Column(db.Integer,
                                   db.ForeignKey('incident_reports.id'))

    def __repr__(self):
        # TODO: Show address instead?
        return 'Coordinates: {0}, {1}'.format(self.latitude, self.longitude)


class IncidentReport(db.Model):
    __tablename__ = 'incident_reports'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(8))
    license_plate = db.Column(db.String(8))
    location = db.relationship('Location',
                               uselist=False,
                               lazy='joined',
                               backref='incident_report')
    date = db.Column(db.DateTime)  # hour the incident occurred
    duration = db.Column(db.Interval)  # like timedelta object
    agency_id = db.Column(db.Integer, db.ForeignKey('agencies.id'))
    picture_url = db.Column(db.Text)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # True if this report's agency will be publicly shown alongside it. That
    # is, when a general user sees a report on the map, this report's agency
    # will only be shown if show_agency_publicly is True. The
    # show_agency_publicly attribute is inherited from a report's agency's
    # is_public field.
    show_agency_publicly = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(IncidentReport, self).__init__(**kwargs)
        if self.agency is not None and 'show_agency_publicly' not in kwargs:
            self.show_agency_publicly = self.agency.is_public

    @staticmethod
    def generate_fake(count=100, **kwargs):
        """Generate a number of fake reports for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice, randint
        from datetime import timedelta
        from faker import Faker
        import random
        import string

        def flip_coin():
            """Returns True or False with equal probability"""
            return choice([True, False])

        def rand_alphanumeric(n):
            """Returns random string of alphanumeric characters of length n"""
            r = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for _ in range(n))
            return r

        agencies = Agency.query.all()
        users = User.query.all()
        fake = Faker()

        seed()
        for i in range(count):
            l = Location(
                original_user_text=fake.address(),
                latitude=str(fake.geo_coordinate(center=39.951021,
                                                 radius=0.001)),
                longitude=str(fake.geo_coordinate(center=-75.197243,
                                                  radius=0.001))
            )
            r = IncidentReport(
                vehicle_id=rand_alphanumeric(6),
                # Either sets license plate to '' or random 6 character string
                license_plate=rand_alphanumeric(6)
                if flip_coin() else '',
                location=l,
                date=fake.date_time_between(start_date="-1y", end_date="now"),
                duration=timedelta(minutes=randint(1, 30)),
                agency=choice(agencies),
                user=choice(users),
                picture_url=fake.image_url(),
                description=fake.paragraph(),
                **kwargs
            )
            db.session.add(r)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
