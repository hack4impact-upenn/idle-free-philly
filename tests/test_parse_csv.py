import unittest
import time
from app import create_app, db
from app.models import User, AnonymousUser, Permission, Role
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
        columns = parse_to_db(db, 'poll244.csv')
        self.assertTrue(columns[0] == 'Timestamp:first')
        self.assertTrue(columns[15] == 'Phone Prefix')