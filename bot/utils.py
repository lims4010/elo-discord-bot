from bot.models import PlayerData


def add_new_user(start_elo, user_id, name, db_UserData, db_UserQueue):
    if db_UserData.count_documents({'user_id': user_id}):
        return False
    else:
        post = {'user_id': user_id,
                'name': name,
                'elo': start_elo,
                'ngames': 0,
                'nwins': 0,
                'nloss': 0}
        db_UserData.insert_one(post)

        post = {'user_id': user_id,
                'inQueue': False,
                'confirmed': False,
                'matchId': 0}
        db_UserQueue.insert_one(post)
        return True


def is_registered(player, db_UserData):
    if db_UserData.count_documents({'name': player}):
        cursor = db_UserData.find({'name': player})
        user_id = cursor[0]['user_id']
        return user_id
    else:
        return None


def in_queue(user_id, db_UserQueue):
    filter = {'user_id': user_id}
    cursor = db_UserQueue.find(filter)
    if cursor[0]['inQueue']:
        return True
    else:
        return False


def change_queue_status(user_id, db_UserQueue):
    db_UserQueue.find_one_and_update({'user_id': user_id},
                                     {'$set': {'inQueue': True}})


def change_confirm_status(message, db_UserQueue):
    user_id = str(message.author.id)
    db_UserQueue.find_one_and_update({'user_id': user_id},
                                     {'$set': {'confirmed': True}})


def is_confirmed(user_id, db_UserQueue):
    filter = {'user_id': user_id}
    cursor = db_UserQueue.find(filter)
    if cursor[0]['confirmed']:
        return True
    else:
        return False


def add_match_queue(message, playerA, playerB, db_UserQueue, db_MatchQueue):
    match = [playerA.__dict__, playerB.__dict__]
    db_MatchQueue.insert_one({'match': match})
    cursor = db_MatchQueue.find({'match': match})
    matchId = cursor[0]['_id']

    db_UserQueue.find_one_and_update({'user_id': playerA.user_id},
                                     {'$set': {'matchId': matchId}})

    db_UserQueue.find_one_and_update({'user_id': playerB.user_id},
                                     {'$set': {'matchId': matchId}})


def get_match(user_id, db_UserQueue, db_MatchQueue):
    cursor = db_UserQueue.find({'user_id': user_id})
    matchId = cursor[0]['matchId']

    cursor = db_MatchQueue.find({'_id': matchId})
    match = cursor[0]['match']

    playerA = convert_to_class(match[0])
    playerB = convert_to_class(match[1])

    return playerA, playerB, matchId


def process_elo(playerA, playerB, db_UserData):
    winsA = playerA.nwins
    winsB = playerB.nwins

    cursorA = db_UserData.find({'user_id': playerA.user_id})
    cursorB = db_UserData.find({'user_id': playerB.user_id})

    eloA = cursorA[0]['elo']
    eloB = cursorB[0]['elo']

    newEloA = calculate_elo(eloA, eloB, winsA, winsB)
    newEloB = calculate_elo(eloB, eloA, winsB, winsA)

    ngamesA = cursorA[0]['ngames']
    ngamesB = cursorB[0]['ngames']

    if ngamesA >= 10:
        db_UserData.find_one_and_update({'user_id': playerB.user_id},
                                        {'$set': {'elo': newEloB}})
    if ngamesB >= 10:
        db_UserData.find_one_and_update({'user_id': playerA.user_id},
                                        {'$set': {'elo': newEloA}})


def calculate_elo(eloA, eloB, winsA, winsB):
    winsA = int(winsA)
    winsB = int(winsB)
    kF = 32
    EA = 1/(1 + 10**((eloB - eloA)/400))
    sumEA = (winsA+winsB) * EA
    SA = winsA
    newEloA = eloA + kF*(SA - sumEA)
    return round(newEloA)


def record_match(playerA, playerB, db_UserData, db_MatchStats):
    sortedMatch = sorted([playerA, playerB], key=lambda x: int(x.user_id))
    playerAId = sortedMatch[0].user_id
    playerBId = sortedMatch[1].user_id
    playerAWins = int(sortedMatch[0].nwins)
    playerBWins = int(sortedMatch[1].nwins)
    ngames = playerAWins + playerBWins
    nameKey = '_'.join([playerAId, playerBId])

    db_UserData.find_one_and_update({'user_id': playerAId},
                                    {'$inc': {'ngames': ngames,
                                              'nwins': playerAWins,
                                              'nloss': playerBWins}})

    db_UserData.find_one_and_update({'user_id': playerBId},
                                    {'$inc': {'ngames': ngames,
                                              'nwins': playerBWins,
                                              'nloss': playerAWins}})

    filter = {'pair': nameKey}
    if db_MatchStats.count_documents(filter):
        cursor = db_MatchStats.find(filter)
        wins = cursor[0]['wins']
        wins[0] = wins[0] + playerAWins
        wins[1] = wins[1] + playerBWins
        db_MatchStats.find_one_and_update(filter,
                                          {'$set': {'wins': wins}})
    else:
        db_MatchStats.insert_one({'pair': nameKey,
                                  'wins': [playerAWins, playerBWins]})


def clear_queue(playerA, playerB, matchId, db_UserQueue, db_MatchQueue):
    db_MatchQueue.find_one_and_delete({'_id': matchId})
    db_UserQueue.find_one_and_update({'user_id': playerA.user_id},
                                     {'$set': {'inQueue': False, 'confirmed': False, 'matchId': 0}})
    db_UserQueue.find_one_and_update({'user_id': playerB.user_id},
                                     {'$set': {'inQueue': False, 'confirmed': False, 'matchId': 0}})


def pull_my_stats(user_id, db_UserData):

    cursor = db_UserData.find({'user_id': user_id})
    elo = cursor[0]['elo']
    ngames = cursor[0]['ngames']
    nwins = cursor[0]['nwins']
    nloss = cursor[0]['nloss']

    return elo, ngames, nwins, nloss


def update_name(user_id, name, db_UserData):
    cursor = db_UserData.find({'user_id': user_id})
    orgName = cursor[0]['name']
    if name == orgName:
        return False
    else:
        db_UserData.find_one_and_update({'user_id': user_id},
                                        {'$set': {'name': name}})
        return True


def pull_vs_stats(playerA, playerB, db_MatchStats):
    sortedMatch = sorted([playerA, playerB], key=lambda x: int(x.user_id))
    playerAId = sortedMatch[0].user_id
    playerBId = sortedMatch[1].user_id
    playerAName = sortedMatch[0].name
    playerBName = sortedMatch[1].name
    nameKey = '_'.join(sorted([playerAId, playerBId]))
    filter = {'pair': nameKey}
    if db_MatchStats.count_documents(filter):
        cursor = db_MatchStats.find(filter)
        wins = cursor[0]['wins']
        return playerAName, playerBName, wins, True
    else:
        return None, None, None, False


def pull_elo_data(db_UserData, nPlayers):
    users = list(db_UserData.find({}))
    names = [user['name'] for user in users]
    elo = [user['elo'] for user in users]

    sortedNames = [y for _, y in sorted(zip(elo, names), reverse=True)]
    sortedElo = sorted(elo, reverse=True)

    sortedNames = sortedNames[:nPlayers]
    sortedElo = sortedElo[:nPlayers]

    return sortedNames, sortedElo


def parse_queue_input(data):

    data = data.split(' ')
    if len(data) != 2:
        return None

    player = PlayerData()
    player.setName(data[0])
    player.setWins(data[1])

    return player


def convert_to_class(obj):
    player = PlayerData()
    player.setName(obj['name'])
    player.setWins(obj['nwins'])
    player.setUserId(obj['user_id'])

    return player
