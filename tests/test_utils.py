from unittest import TestCase, mock
from bot import utils


class RegistrationTests(TestCase):
    def test_add_new_user_false(self):

        db_UserData = mock.Mock()
        db_UserQueue = mock.Mock()

        db_UserData.count_documents.return_value = True

        start_elo = 1500
        user_id = 'test'
        name = 'test'
        flag = utils.add_new_user(
            start_elo, user_id, name, db_UserData, db_UserQueue)

        input_1 = {'user_id': user_id}
        db_UserData.count_documents.assert_called_once_with(input_1)

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

        input_1 = {'user_id': user_id}
        db_UserData.count_documents.assert_called_once_with(input_1)

        input_1 = {'user_id': user_id,
                   'name': name,
                   'elo': start_elo,
                   'ngames': 0,
                   'nwins': 0,
                   'nloss': 0
                   }
        db_UserData.insert_one.assert_called_once_with(input_1)

        input_1 = {'user_id': user_id,
                   'inQueue': False,
                   'confirmed': False,
                   'matchId': 0
                   }
        db_UserQueue.insert_one.assert_called_once_with(input_1)

        self.assertEqual(flag, True)

    def test_is_registered_false(self):

        db_UserData = mock.Mock()

        db_UserData.count_documents.return_value = False

        player = 'test'
        flag, user_id = utils.is_registered(player, db_UserData)

        self.assertEqual(flag, False)

    def test_is_registered_true(self):

        db_UserData = mock.Mock()

        db_UserData.count_documents.return_value = True
        db_UserData.find.return_value = [{'user_id': 'test'}]

        player = 'test'
        flag, user_id = utils.is_registered(player, db_UserData)

        input_1 = {'name': player}
        db_UserData.find.assert_called_once_with(input_1)

        self.assertEqual(user_id, 'test')
        self.assertEqual(flag, True)


class PlayerStatusTests(TestCase):
    def test_in_queue_true(self):

        db_UserQueue = mock.Mock()

        db_UserQueue.find.return_value = [{'inQueue': True}]

        user_id = 'test'
        flag = utils.in_queue(user_id, db_UserQueue)

        self.assertEqual(flag, True)

    def test_in_queue_false(self):

        db_UserQueue = mock.Mock()

        db_UserQueue.find.return_value = [{'inQueue': False}]

        user_id = 'test'
        flag = utils.in_queue(user_id, db_UserQueue)

        self.assertEqual(flag, False)

    def test_change_queue_status(self):

        db_UserQueue = mock.Mock()

        user_id = 'test'
        utils.change_queue_status(user_id, db_UserQueue)

        input_1 = {'user_id': user_id}
        input_2 = {'$set': {'inQueue': True}}
        db_UserQueue.find_one_and_update.assert_called_once_with(
            input_1, input_2)

    def test_change_confirm_status(self):

        message = mock.Mock()
        db_UserQueue = mock.Mock()

        message.author.id = 'test'

        utils.change_confirm_status(message, db_UserQueue)

        input_1 = {'user_id': 'test'}
        input_2 = {'$set': {'confirmed': True}}

        db_UserQueue.find_one_and_update.assert_called_once_with(
            input_1, input_2)

    def test_is_confirmed_true(self):

        db_UserQueue = mock.Mock()

        db_UserQueue.find.return_value = [{'confirmed': True}]

        user_id = 'test'
        flag = utils.is_confirmed(user_id, db_UserQueue)

        self.assertEqual(flag, True)

    def test_is_confirmed_false(self):

        db_UserQueue = mock.Mock()

        db_UserQueue.find.return_value = [{'confirmed': False}]

        user_id = 'test'
        flag = utils.is_confirmed(user_id, db_UserQueue)

        self.assertEqual(flag, False)


class MatchLogicTests(TestCase):
    def test_add_match_queue(self):
