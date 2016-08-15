import unittest
from app import create_app, db
from app.models import IncidentReport, Agency, User


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

    def test_agency_case_insensitive(self):
        db.session.add(Agency(name='sEpTa'))
        db.session.commit()
        agency = Agency.get_agency_by_name('septa')
        self.assertEqual(agency.name, 'SEPTA')

    def test_agency_no_user_no_incident_report(self):
        Agency.insert_agencies()
        agency = Agency.get_agency_by_name('SEPTA')
        self.assertEqual(agency.name, 'SEPTA')
        self.assertTrue(agency.is_official)
        self.assertFalse(agency.is_public)

    def test_agency_with_user_no_incident_report(self):
        Agency.insert_agencies()
        agency = Agency.get_agency_by_name('SEPTA')
        u1 = User(email='user@example.com', password='password')
        u2 = User(email='user2@example.com', password='password')
        agency.users = [u1, u2]
        self.assertEqual(agency.name, 'SEPTA')
        self.assertTrue(agency.is_official)
        self.assertFalse(agency.is_public)
        self.assertEqual(agency.users, [u1, u2])

    def test_agency_with_incident_report_no_user(self):
        Agency.insert_agencies()
        agency = Agency.get_agency_by_name('SEPTA')
        incident1 = IncidentReport(description='Truck idling on the road!',
                                   send_email_upon_creation=False)
        incident2 = IncidentReport(description='Another one!',
                                   send_email_upon_creation=False)
        agency.incident_reports = [incident1, incident2]
        self.assertEqual(agency.name, 'SEPTA')
        self.assertTrue(agency.is_official)
        self.assertFalse(agency.is_public)
        self.assertEqual(agency.incident_reports, [incident1, incident2])
