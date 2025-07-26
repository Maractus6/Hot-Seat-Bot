class GameState:
    def __init__(self, players):
        self.players = players
        self.current_round = 0
        self.current_player_index = 0

        self.questions = []
        self.answer = None
        self.fake_ansswers = {}
        self.guesses = {}
    
    def start_round(self):
        self.questions = []
        self.answer = None
        self.fake_ansswers = {}
        self.guesses = {}

    def get_current_player(self):
        return self.players[self.current_player_index]
    
    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def set_questions(self, questions):
        self.questions == questions

    def set_real_answers(self, answer):
        self.answer = answer

    def record_guess(self, user, answer):
        self.guesses[user] = answer

    def all_fake_answers_collected(self):
        return len(self.fake_ansswers) == (len(self.players) - 1)
    
    def all_guesses_collected(self):
        return len(self.guesses) == (len(self.players) - 1)
    