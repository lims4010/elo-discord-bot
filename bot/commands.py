from bot.utils import parse_queue_input, add_new_user, is_registered, in_queue, change_queue_status, add_match_queue, change_confirm_status, is_confirmed, get_match, process_elo, record_match, clear_queue, pull_my_stats, update_name, pull_vs_stats, pull_elo_data
from bot.models import PlayerData


class Command:

    @classmethod
    def register_user(cls, message, db_UserData, db_UserQueue):
        start_elo = 1500
        user_id = str(message.author.id)
        name = message.author.display_name.lower()

        isNewUser = add_new_user(
            start_elo, user_id, name, db_UserData, db_UserQueue)

        return isNewUser

    @classmethod
    def queue_match(cls, message, command, db_UserData, db_UserQueue, db_MatchQueue):
        name = message.author.display_name.lower()
        if command.count('-') != 1:
            return 'Invalid Input: Too many/little dashes.'

        players = command.split('-')
        if len(players) != 2:
            return 'Invalid Input: Must be two players.'

        players = [x.strip().lower() for x in players]

        playerA = parse_queue_input(players[0])
        playerB = parse_queue_input(players[1])

        if playerA == None or playerB == None:
            return 'Invalid Input: Must be --> PlayerA # - PlayerB #'

        if not (playerA.nwins.isnumeric()) or not (playerB.nwins.isnumeric()):
            return 'Invalid Input: #s must be numeric.'

        if not name in [playerA.name, playerB.name]:
            return 'Invalid. User not in the match.'

        # Match Data: Player[0] -> Discord Display Name, [1] -> # Wins
        # playerA = players[0].split(' ')
        # playerB = players[1].split(' ')

        # if len(playerA) + len(playerB) != 4:
        #     return 'Invalid Input: Must be --> PlayerA # - PlayerB #'
        # if not((playerA[1]+playerB[1]).isnumeric()):
        #     return 'Invalid Input: #s must be numeric.'

        # if not name in [playerA[0], playerB[0]]:
        #     return 'Invalid. User not in the match.'

        userA_id = is_registered(playerA.name, db_UserData)
        userB_id = is_registered(playerB.name, db_UserData)

        if (userA_id == None) and (userB_id == None):
            return 'Players {0} and {1} are not registered.'.format(playerA.name, playerB.name)
        elif (userA_id == None):
            return 'Player {0} not registered.'.format(playerA.name)
        elif (userB_id == None):
            return 'Player {0} not registered.'.format(playerB.name)

        flagA = in_queue(userA_id, db_UserQueue)
        flagB = in_queue(userB_id, db_UserQueue)

        if flagA and flagB:
            return 'Players {0} and {1} are in queue.'.format(playerA.name, playerB.name)
        elif flagA:
            return 'Player {0} already in queue.'.format(playerA.name)
        elif flagB:
            return 'Player {0} already in queue.'.format(playerB.name)

        change_queue_status(userA_id, db_UserQueue)
        change_queue_status(userB_id, db_UserQueue)

        change_confirm_status(message, db_UserQueue)

        # Player[2] -> unique discord user_id

        # playerA.append(userA_id)
        # playerB.append(userB_id)

        playerA.setUserId(userA_id)
        playerB.setUserId(userB_id)

        # Add match to queue
        add_match_queue(message, playerA, playerB, db_UserQueue, db_MatchQueue)

        return 'Match waiting confirmation...'

    @classmethod
    def confirm_match(cls, message, db_UserData,
                      db_UserQueue, db_MatchQueue, db_MatchStats):

        name = message.author.display_name.lower()
        user_id = is_registered(name, db_UserData)

        if (user_id == None):
            return 'Player ' + name + ' not registered.'

        if not (in_queue(user_id, db_UserQueue)):
            return 'Player ' + name + ' not in queue.'

        if is_confirmed(user_id, db_UserQueue):
            return 'Player ' + name + ' already confirmed.'

        playerA, playerB, matchId = get_match(
            user_id, db_UserQueue, db_MatchQueue)

        process_elo(playerA, playerB, db_UserData)

        record_match(playerA, playerB, db_UserData, db_MatchStats)

        clear_queue(playerA, playerB, matchId, db_UserQueue, db_MatchQueue)

        msg = '{0} {1} - {2} {3} match recorded!'.format(
            playerA.name, playerA.nwins, playerB.name, playerB.nwins)

        return msg

    @classmethod
    def cancel_match(cls, message, db_UserData, db_UserQueue, db_MatchQueue):

        name = message.author.display_name.lower()
        user_id = is_registered(name, db_UserData)

        if (user_id == None):
            return 'Player ' + name + ' not registered.'

        if not (in_queue(user_id, db_UserQueue)):
            return 'Player ' + name + ' not in queue.'

        playerA, playerB, matchId = get_match(
            user_id, db_UserQueue, db_MatchQueue)

        clear_queue(playerA, playerB, matchId, db_UserQueue, db_MatchQueue)

        msg = '{0} {1} - {2} {3} match canceled.'.format(
            playerA.name, playerA.nwins, playerB.name, playerB.nwins)

        return msg

    @classmethod
    def get_mystats(cls, message, db_UserData):

        name = message.author.display_name.lower()
        user_id = is_registered(name, db_UserData)

        if (user_id == None):
            return 'Player ' + name + ' not registered.'

        elo, ngames, nwins, nloss = pull_my_stats(
            user_id, db_UserData)

        msg = "{0} stats: {1} ELO, {2} total games, {3} wins, {4} losses.".format(
            name, elo, ngames, nwins, nloss)
        return msg

    @classmethod
    def change_name(cls, message, db_UserData):
        user_id = str(message.author.id)
        name = message.author.display_name.lower()
        flag = update_name(user_id, name, db_UserData)

        if flag:
            return 'Name successfully updated in system.'
        else:
            return 'Name has not changed.'

    @classmethod
    def get_vs_stats(cls, message, command, db_UserData, db_MatchStats):

        name = message.author.display_name.lower()
        userA_id = is_registered(name, db_UserData)
        userB_id = is_registered(command, db_UserData)

        if (userA_id == None) and (userB_id == None):
            return 'Players {0} and {1} are not registered.'.format(name, command)
        elif (userA_id == None):
            return 'Player {0} not registered.'.format(name)
        elif (userB_id == None):
            return 'Player {0} not registered.'.format(command)

        playerA = PlayerData()
        playerB = PlayerData()

        playerA.setName(name)
        playerA.setUserId(userA_id)

        playerB.setName(command)
        playerB.setUserId(userB_id)

        userA_name, userB_name, wins, flag = pull_vs_stats(
            playerA, playerB, db_MatchStats)

        if not flag:
            return 'Matches never played together.'
        else:
            msg = "VS stats: {0} {1} - {2} {3}".format(userA_name,
                                                       wins[0], userB_name, wins[1])
            return msg

    @classmethod
    def queue_status(cls, message, db_UserData,
                     db_UserQueue, db_MatchQueue, db_MatchStats):

        name = message.author.display_name.lower()
        user_id = is_registered(name, db_UserData)

        if (user_id == None):
            return 'Player ' + name + ' not registered.'

        if not (in_queue(user_id, db_UserQueue)):
            return 'Player ' + name + ' not in queue.'

        playerA, playerB, matchId = get_match(
            user_id, db_UserQueue, db_MatchQueue)

        if user_id == playerA.user_id:
            otherPlayer = playerB.name
        else:
            otherPlayer = playerA.name

        flag = is_confirmed(user_id, db_UserQueue)

        if flag:
            msg = 'Game : {0} {1} - {2} {3}, waiting for {4} to confirm'.format(
                playerA.name, playerA.nwins, playerB.name, playerB.nwins, otherPlayer)
        else:
            msg = 'Game : {0} {1} - {2} {3}, waiting for {4} to confirm'.format(
                playerA.name, playerA.nwins, playerB.name, playerB.nwins, name)

        return msg

    @classmethod
    def get_ranking(cls, command, db_UserData):

        params = command.strip().split('-')

        if len(params) > 2:
            return 'Invalid Input.'

        if len(params) == 0 or len(params) == 1:

            nPlayers = 8

        else:

            nPlayers = params[1]

            if nPlayers == 'all':
                nPlayers = None
            elif not nPlayers.isnumeric():
                return 'Invalid Input: - # must be numeric.'
            else:
                nPlayers = int(nPlayers)

        names, elo = pull_elo_data(db_UserData, nPlayers)

        msg = ''

        for idx, val in enumerate(names):
            temp = '{0}. Player : {1} -- ELO : {2} \n'.format(
                idx + 1, names[idx], elo[idx])

            msg = msg + temp

        return msg
