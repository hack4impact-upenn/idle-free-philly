#!/usr/bin/env python
import os
import time
from app import create_app, db
from app.models import (
    User,
    Role,
    Agency,
    Permission,
    IncidentReport,
    EditableHTML
)
from redis import Redis
from rq import Worker, Queue, Connection
from rq_scheduler.scheduler import Scheduler
from rq_scheduler.utils import setup_loghandlers
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from app.parse_csv import parse_to_db


# Import settings from .env file. Must define FLASK_CONFIG
if os.path.exists('.env'):
    print('Importing environment from .env file')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production.
    """
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.option('-nu',
                '--number-users',
                default=10,
                type=int,
                help='Number of users to create',
                dest='number_users')
@manager.option('-nr',
                '--number-reports',
                default=100,
                type=int,
                help='Number of reports to create',
                dest='number_reports')
def add_fake_data(number_users, number_reports):
    """
    Adds fake data to the database.
    """
    User.generate_fake(count=number_users)
    IncidentReport.generate_fake(count=number_reports)


@manager.command
def setup_dev():
    """Runs the set-up needed for local development."""
    setup_general()

    # Create a default admin user
    admin = User(email='admin@user.com',
                 phone_number='+12345678910',
                 password='password',
                 first_name='Admin',
                 last_name='User',
                 role=Role.query.filter_by(permissions=Permission.ADMINISTER)
                 .first(),
                 confirmed=True)

    # Create a default agency worker user
    worker = User(email='agency@user.com',
                  phone_number='+11098764321',
                  password='password',
                  first_name='AgencyWorker',
                  last_name='User',
                  role=Role.query
                  .filter_by(permissions=Permission.AGENCY_WORKER)
                  .first(),
                  confirmed=True)
    worker.agencies = [Agency.get_agency_by_name('SEPTA')]

    # Create a default general user
    general = User(email='general@user.com',
                   phone_number='+15434549876',
                   password='password',
                   first_name='General',
                   last_name='User',
                   role=Role.query.filter_by(permissions=Permission.GENERAL)
                   .first(),
                   confirmed=True)

    db.session.add(admin)
    db.session.add(worker)
    db.session.add(general)

    db.session.commit()


@manager.option('-f',
                '--filename',
                default='poll244.csv',
                type=str,
                help='Filename of csv to parse',
                dest='filename')
def parse_csv(filename):
    """Parses the given csv file into the database."""
    parse_to_db(db, filename)


@manager.command
def setup_prod():
    """Runs the set-up needed for production."""
    setup_general()


def setup_general():
    """Runs the set-up needed for both local development and production."""
    Role.insert_roles()
    Agency.insert_agencies()
    EditableHTML.add_default_faq()


@manager.command
def run_worker():
    """Initializes a slim rq task queue."""
    listen = ['default']
    conn = Redis(
        host=app.config['RQ_DEFAULT_HOST'],
        port=app.config['RQ_DEFAULT_PORT'],
        db=0,
        password=app.config['RQ_DEFAULT_PASSWORD']
    )

    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()


@manager.command
def run_scheduler():
    """Initializes a rq scheduler."""
    conn = Redis(
        host=app.config['RQ_DEFAULT_HOST'],
        port=app.config['RQ_DEFAULT_PORT'],
        db=0,
        password=app.config['RQ_DEFAULT_PASSWORD']
    )

    setup_loghandlers('INFO')
    scheduler = Scheduler(connection=conn, interval=60.0)
    for _ in xrange(10):
        try:
            scheduler.run()
        except ValueError as exc:
            if exc.message == 'There\'s already an active RQ scheduler':
                scheduler.log.info(
                    'An RQ scheduler instance is already running. Retrying in '
                    '%d seconds.', 10,
                )
                time.sleep(10)
            else:
                raise exc


if __name__ == '__main__':
    manager.run()
