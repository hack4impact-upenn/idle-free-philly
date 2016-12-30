import pytz
import traceback

from datetime import datetime, timedelta
from flask import current_app
from flask.ext.rq import get_queue
from .. import db
from . import Agency, User
from ..email import send_email
from ..utils import get_current_weather, url_for_external


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))
    # TODO: ensure original_user_text is always non-null
    original_user_text = db.Column(db.Text)  # the raw text which we geocoded
    incident_report_id = db.Column(db.Integer,
                                   db.ForeignKey('incident_reports.id'))

    def __repr__(self):
        return str(self.original_user_text)


class IncidentReport(db.Model):
    __tablename__ = 'incident_reports'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(50))
    license_plate = db.Column(db.String(50))  # optional
    bus_number = db.Column(db.Integer)  # optional
    led_screen_number = db.Column(db.Integer)  # optional
    location = db.relationship('Location',
                               uselist=False,
                               lazy='joined',
                               backref='incident_report')
    date = db.Column(db.DateTime)  # datetime object
    duration = db.Column(db.Interval)  # timedelta object
    agency_id = db.Column(db.Integer, db.ForeignKey('agencies.id'))
    picture_url = db.Column(db.Text)

    # Should never be exposed to the user. This is the Imgur deletehash, so
    # we can delete an image from Imgur in case of problems (e.g.
    # legal issues).
    picture_deletehash = db.Column(db.Text)
    description = db.Column(db.Text)
    weather = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # True if this report's agency will be publicly shown alongside it. That
    # is, when a general user sees a report on the map, this report's agency
    # will only be shown if show_agency_publicly is True. The
    # show_agency_publicly attribute is inherited from a report's agency's
    # is_public field.
    show_agency_publicly = db.Column(db.Boolean, default=False)

    def __init__(self, send_email_upon_creation=True, **kwargs):
        super(IncidentReport, self).__init__(**kwargs)
        if self.agency is not None and 'show_agency_publicly' not in kwargs:
            self.show_agency_publicly = self.agency.is_public

        if self.date is None:
            self.date = datetime.now(pytz.timezone(
                current_app.config['TIMEZONE']))
            self.date = self.date.replace(tzinfo=None)

        now = datetime.now(pytz.timezone(
                current_app.config['TIMEZONE'])).replace(tzinfo=None)
        if self.weather is None and self.location is not None and \
                (now - self.date < timedelta(minutes=1)):
            self.weather = get_current_weather(self.location)

        self.description = self.description.replace('\n', ' ').strip()
        self.description = self.description.replace('\r', ' ').strip()

        if send_email_upon_creation:
            all_reports_for_agency_link = url_for_external(
                'reports.view_reports')
            index_page_link = url_for_external(
                'main.index')
            subject = '{} Idling Incident'.format(self.agency.name)

            if self.location.original_user_text is not None:
                subject += ' at {}'.format(self.location.original_user_text)

            for agency_worker in self.agency.users:
                get_queue().enqueue(
                    send_email,
                    recipient=agency_worker.email,
                    subject=subject,
                    template='reports/email/alert_workers',
                    incident_report=self,
                    user=agency_worker.full_name(),
                    all_reports_for_agency_link=all_reports_for_agency_link,
                    index_page_link=index_page_link
                )

            if current_app.config['SEND_ALL_REPORTS_TO']:
                get_queue().enqueue(
                    send_email,
                    recipient=current_app.config['SEND_ALL_REPORTS_TO'],
                    subject=subject,
                    template='reports/email/alert_workers',
                    incident_report=self,
                    user=current_app.config['SEND_ALL_REPORTS_TO'],
                    all_reports_for_agency_link=all_reports_for_agency_link,
                    index_page_link=index_page_link
                )

        traceback.print_stack()  # TODO: Remove
        print locals()

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
                                                 radius=0.01)),
                longitude=str(fake.geo_coordinate(center=-75.197243,
                                                  radius=0.01))
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
                send_email_upon_creation=False,
                **kwargs
            )
            db.session.add(r)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
