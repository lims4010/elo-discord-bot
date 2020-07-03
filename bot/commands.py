from utils import is_registered, in_queue, add_match_queue


class Command:

    @classmethod
    def register_user(cls, message, db_UserData, db_UserQueue):
        start_elo = 1500
        user_id = message.author.id
        name = message.author.display_name.lower()
        if db_UserData.count_documents({'user_id': user_id}):
            return False
        else:
            post = {'user_id': user_id,
                    'name': name,
                    'elo': start_elo,
                    'nwins': 0,
                    'nloss': 0}
            db_UserData.insert_one(post)

            post = {'name': name,
                    'inQueue': False,
                    'confirmed': False,
                    'matchId': 0}
            db_UserQueue.insert_one(post)
            return True

    @classmethod
    def queue_match(cls, message, command, db_UserData, db_UserQueue, db_MatchQueue):
        if command.count('-') != 1:
            return 'Invalid Input: Too many dashes.'

        players = command.split('-')
        if len(players) != 2:
            return 'Invalid Input: # of players.'

        players = [x.strip().lower() for x in players]

        # Match Data: Player[0] -> Discord Display Name, [1] -> # Wins
        playerA = players[0].split(' ')
        playerB = players[1].split(' ')

        if len(playerA) + len(playerB) != 4:
            return 'Invalid Input: Must be --> PlayerA # - PlayerB #'
        if not((playerA[1]+playerB[1]).isnumeric()):
            return 'Invalid Input: #s must be numeric.'

        if not(is_registered(playerA, db_UserData)):
            return 'Player ' + playerA[0] + ' not registered.'

        if not(is_registered(playerB, db_UserData)):
            return 'Player ' + playerB[0] + ' not registered.'

        if in_queue(playerA, db_UserQueue):
            return 'Player ' + playerA[0] + ' in queue.'

        if in_queue(playerB, db_UserQueue):
            return 'Player ' + playerB[0] + ' in queue.'

        add_match_queue(message, playerA, playerB, db_UserQueue, db_MatchQueue)

        return 'Match waiting confirmation...'
