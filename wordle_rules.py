import random
from database import Database


WORD_FILES_DIRECTORY = "word_files"
WORD_FILES = {
    3: "three_letters.txt",
    4: "four_letters.txt",
    5: "five_letters.txt",
    6: "six_letters.txt",
}
MIN_WORD_LENGTH = 3
MAX_WORD_LENGTH = 6
MIN_HIGH_SCORE = 0
MAX_HIGH_SCORE = None


class WordleRules:
    def __init__(self):
        self.min_word_length = MIN_WORD_LENGTH
        self.max_word_length = MAX_WORD_LENGTH
        self.min_high_score = MIN_HIGH_SCORE
        self.max_high_score = MAX_HIGH_SCORE
        self._db = Database()
        self.word_length, self.high_score = self._db.get_data()
        self.max_guesses = self.word_length + 1
        self.word = ""
        self._words_list = []
        self._used_words = []
        self._guess = ""
        self._guess_count = 0
        self._guess_eval = ["x" for _ in range(self.word_length)]
        self._load_words()
        self.select_word()

    def _load_words(self):
        word_file = f"{WORD_FILES_DIRECTORY}/{WORD_FILES[self.word_length]}"
        with open(word_file, "r") as file:
            self._words_list = file.readlines()
        self._words_list = [word.strip("\n") for word in self._words_list]
        self._used_words = []

    def calculate_score(self):
        score = 2 * (self.max_guesses - (self._guess_count - 1))
        if score > self.high_score:
            self.high_score = score
            self._db.set_high_score(score)
        return score

    def get_letter_status(self, i):
        if self._guess_eval[i] == "=":
            return "lvl2"
        if self._guess_eval[i] == "*":
            return "lvl1"
        return "lvl0"

    def is_guess_correct(self):
        return self._guess == self.word

    def is_valid_word(self, guess):
        if guess.lower() in self._words_list:
            return True
        return False

    def new_rules(self, word_length, high_score):
        if word_length != self.word_length or high_score != self.high_score:
            self._db.set_data(word_length, high_score)
            self.high_score = high_score
            if word_length != self.word_length:
                self.word_length = word_length
                self.max_guesses = self.word_length + 1
                self._load_words()

    def out_of_guesses(self):
        return self._guess_count >= self.max_guesses

    def select_word(self):
        self.word = random.choice(self._words_list).upper()
        while self.word in self._used_words:
            self.word = random.choice(self._words_list).upper()
        self._used_words.append(self.word)
        self._guess = ""
        self._guess_count = 0
        self._guess_eval = ["x" for _ in range(self.word_length)]

    def submit_guess(self, guess):
        self._guess_count += 1
        self._guess = guess
        g = list(self._guess)
        w = list(self.word)
        self._guess_eval = ["x" for _ in range(self.word_length)]
        for i in range(self.word_length):
            if g[i] == w[i]:
                self._guess_eval[i] = w[i] = g[i] = "="
        for i in range(self.word_length):
            if g[i] != "=" and g[i] != "*":
                for j in range(self.word_length):
                    if g[i] == w[j]:
                        self._guess_eval[i] = w[j] = g[i] = "*"
                        break
