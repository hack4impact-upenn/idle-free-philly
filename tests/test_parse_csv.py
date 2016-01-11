import unittest
from app import create_app, db
from app.models import Location, IncidentReport
from app.parse_csv import parse_to_db


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
        columns = parse_to_db(db, 'tests/poll244_sample.csv')
        self.assertTrue(columns[0] == 'Timestamp:first')
        self.assertTrue(columns[15] == 'Phone Prefix')

    def test_parse_into_db_location(self):
        parse_to_db(db, 'tests/poll244_sample.csv')
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
        parse_to_db(db, 'tests/poll244_sample.csv')
        t_url = 'https://textizen-attachments.s3.amazonaws.com/'

        license1 = 'AG26081'
        vehicle1 = '250'
        agency1 = 'ABBONIZIO TRANSFER'
        duration1 = '0:03:00'
        pic1 = t_url+'uploads/response/photo_attachment/255089/IMG_2937.jpg'
        desc1 = 'Driver in truck, possibly eating, windows partially down'
        i1 = IncidentReport.query.filter_by(license_plate=license1).first()
        self.assertTrue(i1.vehicle_id == vehicle1)
        self.assertTrue(i1.agency.name == agency1)
        self.assertTrue(str(i1.duration) == duration1)
        self.assertTrue(i1.picture_url == pic1)
        self.assertTrue(i1.description == desc1)

        license2 = 'YSK9618'
        vehicle2 = '220530591'
        agency2 = 'VERIZON'
        duration2 = '0:05:00'
        pic2 = t_url+'uploads/response/photo_attachment/255080/IMG_3656.jpg'
        desc2 = 'Driver sleeping in truck, no work being done.'
        i2 = IncidentReport.query.filter_by(license_plate=license2).first()
        self.assertTrue(i2.vehicle_id == vehicle2)
        self.assertTrue(i2.agency.name == agency2)
        self.assertTrue(str(i2.duration) == duration2)
        self.assertTrue(i2.picture_url == pic2)
        self.assertTrue(i2.description == desc2)

        license3 = 'MG0512E'
        vehicle3 = '105014'
        agency3 = 'STREETS'
        duration3 = '0:06:00'
        pic3 = t_url+'uploads/response/photo_attachment/255071/IMG_5074.jpg'
        desc3 = 'Driver in truck talking on phone, window partially down,' + \
            ' no work being done'
        i3 = IncidentReport.query.filter_by(license_plate=license3).first()
        self.assertTrue(i3.vehicle_id == vehicle3)
        self.assertTrue(i3.agency.name == agency3)
        self.assertTrue(str(i3.duration) == duration3)
        self.assertTrue(i3.picture_url == pic3)
        self.assertTrue(i3.description == desc3)
