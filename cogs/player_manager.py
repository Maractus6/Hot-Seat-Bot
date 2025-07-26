class PlayerManager:
    def __init__(self):
        self.players = []

    def add_player(self, user):
        if user not in self.players:
            self.players.append(user)
            return True
        return False

    def remove_player(self, user):
        if user in self.players:
            self.players.remove(user)
            return True
        return False

    def get_players(self):
        return self.players

    def has_enough_players(self):
        return len(self.players) >= 3