from unittest import TestCase, mock
from bot import utils


class UtilsTestCase(TestCase):
    def test_add_new_user_false(self):

        db_UserData = mock.Mock()
        db_UserQueue = mock.Mock()

        db_UserData.count_documents.return_value = True

        start_elo = 1500
        user_id = 'test'
        name = 'test'

        flag = utils.add_new_user(
            start_elo, user_id, name, db_UserData, db_UserQueue)

        post = {'user_id': user_id}
        db_UserData.count_documents.assert_called_once_with(post)

        self.assertEqual(flag, False)

    def test_add_new_user_true(self):

        db_UserData = mock.Mock()
        db_UserQueue = mock.Mock()

        db_UserData.count_documents.return_value = False

        start_elo = 1500
        user_id = 'test'
        name = 'test'

        flag = utils.add_new_user(
            start_elo, user_id, name, db_UserData, db_UserQueue)

        post = {'user_id': user_id,
                'name': name,
                'elo': start_elo,
                'ngames': 0,
                'nwins': 0,
                'nloss': 0
                }

        db_UserData.insert_one.assert_called_once_with(post)

        post = {'user_id': user_id,
                'inQueue': False,
                'confirmed': False,
                'matchId': 0
                }

        db_UserQueue.insert_one.assert_called_once_with(post)

        self.assertEqual(flag, True)
