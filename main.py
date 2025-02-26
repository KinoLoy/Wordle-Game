from wordle_board import WordleBoard
from wordle_rules import WordleRules

if __name__ == '__main__':
    rules = WordleRules()
    board = WordleBoard(rules)
    board.mainloop()
