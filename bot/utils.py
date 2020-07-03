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
        return True, user_id
    else:
        return False, None


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


def add_match_queue(message, playerA, playerB, db_UserQueue, db_MatchQueue):
    # match = sorted([playerA, playerB])
    match = [playerA, playerB]
    db_MatchQueue.insert_one({'match': match})
    cursor = db_MatchQueue.find({'match': match})
    matchId = cursor[0]['_id']

    db_UserQueue.find_one_and_update({'user_id': playerA[2]},
                                     {'$set': {'matchId': matchId}})

    db_UserQueue.find_one_and_update({'user_id': playerB[2]},
                                     {'$set': {'matchId': matchId}})


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


def get_match(user_id, db_UserQueue, db_MatchQueue):
    cursor = db_UserQueue.find({'user_id': user_id})
    matchId = cursor[0]['matchId']

    cursor = db_MatchQueue.find({'_id': matchId})
    match = cursor[0]['match']

    return match[0], match[1], matchId


def process_elo(playerA, playerB, db_UserData):
    winsA = playerA[1]
    winsB = playerB[1]

    cursorA = db_UserData.find({'user_id': playerA[2]})
    cursorB = db_UserData.find({'user_id': playerB[2]})

    eloA = cursorA[0]['elo']
    eloB = cursorB[0]['elo']

    newEloA = calculate_elo(eloA, eloB, winsA, winsB)
    newEloB = calculate_elo(eloB, eloA, winsB, winsA)

    ngamesA = cursorA[0]['ngames']
    ngamesB = cursorB[0]['ngames']

    if ngamesA > 10:
        db_UserData.find_one_and_update({'user_id': playerB[2]},
                                        {'$set': {'elo': newEloB}})
    if ngamesB > 10:
        db_UserData.find_one_and_update({'user_id': playerA[2]},
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
    sortedMatch = sorted([playerA, playerB], key=lambda x: int(x[2]))
    # sortedMatch = sorted([playerA[0], playerB[0]])
    # playerAName = sortedMatch[0][1]
    # playerBName = sortedMatch[1][1]
    playerAId = sortedMatch[0][2]
    playerBId = sortedMatch[1][2]
    playerAWins = int(sortedMatch[0][1])
    playerBWins = int(sortedMatch[1][1])
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
    db_UserQueue.find_one_and_update({'user_id': playerA[2]},
                                     {'$set': {'inQueue': False, 'confirmed': False, 'matchId': 0}})
    db_UserQueue.find_one_and_update({'user_id': playerB[2]},
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
    sortedMatch = sorted([playerA, playerB], key=lambda x: int(x[1]))
    playerAId = sortedMatch[0][1]
    playerBId = sortedMatch[1][1]
    playerAName = sortedMatch[0][0]
    playerBName = sortedMatch[1][0]
    nameKey = '_'.join(sorted([playerAId, playerBId]))
    filter = {'pair': nameKey}
    if db_MatchStats.count_documents(filter):
        cursor = db_MatchStats.find(filter)
        wins = cursor[0]['wins']
        return playerAName, playerBName, wins, True
    else:
        return None, None, None, False
