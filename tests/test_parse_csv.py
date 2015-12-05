import unittest
from app import create_app, db
from app.models import Location, IncidentReport
from app.utils import parse_to_db


class ParseCsvTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_EVERYTHING(self):
        columns = parse_to_db(db, 'poll244.csv')
