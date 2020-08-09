class PlayerData:
    def __init__(self):
        self.name = None
        self.nwins = None
        self.user_id = None

    def setName(self, name):
        self.name = name

    def setWins(self, wins):
        self.nwins = wins

    def setUserId(self, user_id):
        self.user_id = user_id
