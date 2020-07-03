def is_registered(player, db_UserData):
    if db_UserData.count_documents({'name': player[0]}):
        return True
    else:
        return False


def in_queue(player, db_UserQueue):
    filter = {'name': player[0]}
    cursor = db_UserQueue.find(filter)
    if cursor[0]['inQueue']:
        return True
    else:
        db_UserQueue.find_one_and_update(filter,
                                         {'$set': {'inQueue': True}})
        return False


def add_match_queue(message, playerA, playerB, db_UserQueue, db_MatchQueue):
    match = sorted([playerA, playerB])
    db_MatchQueue.insert_one({'match': match})
    cursor = db_MatchQueue.find({'match': match})
    matchId = cursor[0]['_id']

    db_UserQueue.find_one_and_update({'name': playerA[0]},
                                     {'$set': {'matchId': id}})

    db_UserQueue.find_one_and_update({'name': playerB[0]},
                                     {'$set': {'matchId': id}})

    name = message.author.display_name.lower()
    db_UserQueue.find_one_and_update({'name': name},
                                     {'$set': {'confirmed': True}})
