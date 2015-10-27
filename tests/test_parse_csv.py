import unittest
import time
from app import create_app, db
from app.models import Location, IncidentReport
from app.utils import *

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

    def test_parse_columns(self):
        columns = parse_to_db(db, 'poll244_sample.csv')
        self.assertTrue(columns[0] == 'Timestamp:first')
        self.assertTrue(columns[15] == 'Phone Prefix')

    def test_parse_into_db_location(self):
        parse_to_db(db, 'poll244_sample.csv')
        loc1_text = '15 & chestnut'
        loc1 = Location.query.filter_by(original_user_text=loc1_text).first()
        # Check that geocoded coordinates match expected
        #self.assertTrue(loc1.latitude > ... and loc1.latitude < .....)
        #self.assertTrue(loc1.longitude > ... and loc1.longitude < .....)

    def test_parse_into_db_incident(self):
        parse_to_db(db, 'poll244_sample.csv')
        incident1_license = 'AG-26081'
        incident1 = IdlingIncident.query\
            .filter_by(license_plate=incident1_license).first()
        self.assertTrue(incident1.vehicle_id == '250')
        self.assertTrue(incident1.license_plate == 'AG-26081')
        address = incident1.location.original_user_text
        self.assertTrue(address == '15 & chestnut')
