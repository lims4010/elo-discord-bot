from bot.utils import add_new_user, is_registered, in_queue, change_queue_status, add_match_queue, is_confirmed, get_match, process_elo, record_match, clear_queue, pull_my_stats, update_name, pull_vs_stats


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

        flagA, userA_id = is_registered(playerA[0], db_UserData)
        flagB, userB_id = is_registered(playerB[0], db_UserData)

        if not(flagA):
            return 'Player ' + playerA[0] + ' not registered.'

        if not(flagB):
            return 'Player ' + playerB[0] + ' not registered.'

        if in_queue(userA_id, db_UserQueue):
            return 'Player ' + playerA[0] + ' in queue.'

        if in_queue(userB_id, db_UserQueue):
            return 'Player ' + playerB[0] + ' in queue.'

        change_queue_status(userA_id, db_UserQueue)
        change_queue_status(userB_id, db_UserQueue)

        # Player[2] -> unique discord user_id

        playerA.append(userA_id)
        playerB.append(userB_id)

        add_match_queue(message, playerA, playerB, db_UserQueue, db_MatchQueue)

        return 'Match waiting confirmation...'

    @classmethod
    def confirm_match(cls, message, command, db_UserData,
                      db_UserQueue, db_MatchQueue, db_MatchStats):

        name = message.author.display_name.lower()
        flag, user_id = is_registered(name, db_UserData)

        if not(flag):
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
            playerA[0], playerA[1], playerB[0], playerB[1])

        return msg

    @classmethod
    def get_mystats(cls, message, db_UserData):

        name = message.author.display_name.lower()
        flag, user_id = is_registered(name, db_UserData)

        if not(flag):
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
        flagA, userA_id = is_registered(name, db_UserData)
        flagB, userB_id = is_registered(command, db_UserData)

        if not(flagA):
            return 'Player ' + name + ' not registered.'
        if not(flagB):
            return 'Player ' + command + ' not registered.'

        userA_name, userB_name, wins, flag = pull_vs_stats(
            [name, userA_id], [command, userB_id], db_MatchStats)

        if not flag:
            return 'Matches never played together.'
        else:
            msg = "VS stats: {0} {1} - {2} {3}".format(userA_name,
                                                       wins[0], userB_name, wins[1])
            return msg
