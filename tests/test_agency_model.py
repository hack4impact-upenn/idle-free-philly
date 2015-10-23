import unittest
from app import create_app, db
from app.models import IncidentReport, Agency


class AgencyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_agency_no_user_no_incident_report(self):
        agency = Agency(
            name='SEPTA',
            is_official=True,
            is_public=False,
        )
        self.assertEqual(agency.name, 'SEPTA')
        self.assertTrue(agency.is_official)
        self.assertFalse(agency.is_public)
