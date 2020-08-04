from unittest import TestCase, mock
from bot import utils


class UtilsTestCase(TestCase):

    def test_add_new_user(self):
        db = mock.Mock()
        start_elo = 500
        user_id = 'test'
        name = 'test'
        flag = utils.add_new_user(start_elo, user_id, name, db, db)
        self.assertIsNotNone(flag)
