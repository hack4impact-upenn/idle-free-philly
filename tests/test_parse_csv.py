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
        loc1_text = '15 & chestnut '
        loc1 = Location.query.filter_by(original_user_text=loc1_text).first()
        # Check that geocoded coordinates match expected 39.951304, -75.165601
        self.assertAlmostEqual(float(loc1.latitude), 39.951304, places=3)
        self.assertAlmostEqual(float(loc1.longitude), -75.165601, places=3)

        loc2_text = 'Poplar & n American '
        loc2 = Location.query.filter_by(original_user_text=loc2_text).first()
        # Check that geocoded coordinates match expected 39.964792, -75.141594
        self.assertAlmostEqual(float(loc2.latitude), 39.964792, places=3)
        self.assertAlmostEqual(float(loc2.longitude), -75.141594, places=3)

        loc3_text = 'Broad & arch '
        loc3 = Location.query.filter_by(original_user_text=loc3_text).first()
        # Check that geocoded coordinates match expected 39.954659, -75.163059
        self.assertAlmostEqual(float(loc3.latitude), 39.954659, places=3)
        self.assertAlmostEqual(float(loc3.longitude), -75.163059, places=3)

    def test_parse_into_db_incident(self):
        parse_to_db(db, 'poll244_sample.csv')
        incident1_license = 'AG-26081'
        incident1 = IncidentReport.query.filter_by(license_plate=incident1_license).first()
        self.assertTrue(incident1.vehicle_id == '250')
        self.assertTrue(incident1.agency.name == 'ABBONIZIO TRANSFER')
        self.assertTrue(str(incident1.duration) == '0:03:00')
        pic_url1 = 'https://textizen-attachments.s3.amazonaws.com/uploads/response/photo_attachment/255089/IMG_2937.jpg'
        self.assertTrue(incident1.picture_url == pic_url1)
        self.assertTrue(incident1.description == 'Driver in truck, possibly eating, windows partially down')

        incident2_license = 'YSK-9618'
        incident2 = IncidentReport.query.filter_by(license_plate=incident2_license).first()
        self.assertTrue(incident2.vehicle_id == '220530591')
        self.assertTrue(incident2.agency.name == 'VERIZON')
        self.assertTrue(str(incident2.duration) == '0:05:00')
        pic_url2 = 'https://textizen-attachments.s3.amazonaws.com/uploads/response/photo_attachment/255080/IMG_3656.jpg'
        self.assertTrue(incident2.picture_url == pic_url2)
        self.assertTrue(incident2.description == 'Driver sleeping in truck, no work being done.')

        incident3_license = 'MG-0512E'
        incident3 = IncidentReport.query.filter_by(license_plate=incident3_license).first()
        self.assertTrue(incident3.vehicle_id == '105014')
        self.assertTrue(incident3.agency.name == 'STREETS')
        self.assertTrue(str(incident3.duration) == '0:06:00')
        pic_url3 = 'https://textizen-attachments.s3.amazonaws.com/uploads/response/photo_attachment/255071/IMG_5074.jpg'
        self.assertTrue(incident3.picture_url == pic_url3)
        description3 = 'Driver in truck talking on phone, window partially down, no work being done'
        self.assertTrue(incident3.description == description3)