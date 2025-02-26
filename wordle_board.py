import tkinter as tk
from PIL import Image, ImageTk
import ctypes
import ui


ctypes.windll.shcore.SetProcessDpiAwareness(1)


class WordleBoard(tk.Tk):
    def __init__(self, wordle_rules):
        super().__init__()
        self.rules = wordle_rules
        self.score = 0
        self.won = False
        self.guess = ""
        self.guess_row = 0
        self.guess_col = 0
        # hide window during construction
        self.withdraw()
        self.tk_setPalette(
            background=ui.color["base"]["pri"]["bg"],
            foreground=ui.color["base"]["pri"]["fg"],
        )
        self.wm_iconbitmap('images/icon.ico')
        self.title("Wordle")
        self.width = 500
        self.height = 700
        self.x_co = int(self.winfo_screenwidth() / 2) - int(self.width / 2)
        self.y_co = 50
        self.geometry(f"{self.width}x{self.height}+{self.x_co}+{self.y_co}")
        self.bind("<KeyRelease>", self.key_press)
        self.menu = self.MenuBar(self)
        self.title_ = self.TitleBar(self)
        self.grid = self.GuessGrid(self)
        self.vkb = self.VirtualKeyboard(self)
        self.status_bar = self.StatusBar(self)
        # unveil window
        self.update_idletasks()
        self.deiconify()

    def check_for_match(self):
        self.status_bar["text"] = f"Score : {self.score}"
        if len(self.guess) == self.rules.word_length:
            if not self.rules.is_valid_word(self.guess):
                self.status_bar["text"] = "Word is not in dictionary!"
                return
            self.rules.submit_guess(self.guess)
            for i in range(self.rules.word_length):
                status = self.rules.get_letter_status(i)
                self.grid.set_status(self.guess_row, i, status)
                self.vkb.set_key_status(self.guess[i], status)
            if self.rules.is_guess_correct():
                self.won = True
                self.score += self.rules.calculate_score()
                self.status_bar["text"] = f"Score : {self.score}"
                go = self.GameOver(self)
            else:
                if self.rules.out_of_guesses():
                    go = self.GameOver(self)
                else:
                    # prep for the next guess
                    self.guess = ""
                    self.guess_row += 1
                    self.guess_col = 0

    def erase_character(self):
        if self.guess_col > 0:
            self.guess_col -= 1
            self.guess = self.guess[0: self.guess_col]
            self.grid.reset_guess(self.guess_row, self.guess_col)

    def key_press(self, event):
        if event:
            if event.keysym == "Return":
                self.check_for_match()
            elif event.keysym == "BackSpace":
                self.erase_character()
            elif 65 <= event.keycode <= 90:
                key = event.char.upper()
                if self.guess_col == self.rules.word_length:
                    self.erase_character()
                self.grid.set_guess(self.guess_row, self.guess_col, key)
                self.guess += key
                self.guess_col += 1

    def reset_board(self, gameover=None):
        self.rules.select_word()
        self.grid.reset_guesses()
        self.vkb.reset_keys()
        # win streak ended, reset score to zero
        if not self.won:
            self.score = 0
        self.won = False
        self.guess = ""
        self.guess_row = 0
        self.guess_col = 0
        self.status_bar["text"] = f"Score : {self.score}"
        if gameover:
            self.attributes('-disabled', False)
            self.focus_get()
            gameover.destroy()

    def reset_rules(self, settings=None):
        self.rules.select_word()
        self.grid.destroy()
        self.vkb.destroy()
        self.grid = self.GuessGrid(self)
        self.vkb = self.VirtualKeyboard(self)
        self.score = 0
        self.won = False
        self.guess = ""
        self.guess_row = 0
        self.guess_col = 0
        self.status_bar["text"] = f"Score : {self.score}"
        if settings:
            self.attributes('-disabled', False)
            self.focus_get()
            settings.destroy()


    class GuessGrid(tk.Frame):
        def __init__(self, parent):
            super().__init__(parent)
            self._parent = parent
            self._word_length = parent.rules.word_length
            self._max_guesses = parent.rules.max_guesses
            self.pack(pady=15)
            self.guess_rows = [
                tk.Frame(self) for _ in range(self._max_guesses)
            ]
            self.guesses = []
            for i in range(self._max_guesses):
                self.guess_rows[i].pack(pady=4)
                word = []
                for j in range(self._word_length):
                    letter = parent.GuessLetterBox(self.guess_rows[i])
                    word.append(letter)
                self.guesses.append(word)

        def reset_guess(self, i, j):
            self.guesses[i][j].reset_letter_box()

        def reset_guesses(self):
            for word in self.guesses:
                for letter in word:
                    letter.reset_letter_box()

        def set_guess(self, i, j, letter):
            self.guesses[i][j]["text"] = letter

        def set_status(self, i, j, status):
            self.guesses[i][j].set_letter_box_status(status)


    class GuessLetterBox(tk.Button):
        def __init__(self, parent):
            super().__init__(parent)
            self.config(
                font=ui.font["guess"],
                text="",
                width=3,
                height=1,
                bd=1.25,
                relief="solid",
                default="disabled",
                takefocus=False,
            )
            self.pack(side="left", padx=3)

        def reset_letter_box(self):
            self["text"] = ""
            self['bg'] = ui.color["base"]["pri"]["bg"]
            self['fg'] = ui.color["base"]["pri"]["fg"]

        def set_letter_box_status(self, status):
            self['bg'] = ui.color[status]["pri"]["bg"]
            self['fg'] = ui.color[status]["pri"]["fg"]


    class MenuBar(tk.Frame):
        def __init__(self, parent):
            super().__init__(parent)
            self._parent = parent
            self.pack(fill="x")
            i = Image.open('images/setting.png')
            i = i.resize((40, 40), Image.Resampling.LANCZOS)
            self.setting = ImageTk.PhotoImage(i)
            i = Image.open('images/setting_dark.png')
            i = i.resize((40, 40), Image.Resampling.LANCZOS)
            self.setting_dark = ImageTk.PhotoImage(i)
            settings = tk.Button(
                self,
                image=self.setting,
                command=self.open_settings,
                bd=0,
                cursor="hand2",
            )
            settings.pack(side="right")
            settings.bind("<Enter>", self.settings_on_hover)
            settings.bind("<Leave>", self.settings_off_hover)

        def open_settings(self):
            s = self._parent.Settings(self._parent)

        def settings_on_hover(self, event):
            event.widget["image"] = self.setting_dark

        def settings_off_hover(self, event):
            event.widget["image"] = self.setting


    class StatusBar(tk.Label):
        def __init__(self, parent):
            super().__init__(parent)
            self.config(
                text=f"Score : {parent.score}",
                font=ui.font["status"],
                bg=ui.color["base"]["pri"]["fg"],
                fg=ui.color["base"]["pri"]["bg"],
                anchor="w",
                padx=10,
            )
            self.pack(fill='x', side="bottom")


    class TitleBar(tk.Label):
        def __init__(self, parent):
            super().__init__(parent)
            i = Image.open('images/head.png')
            self.title_image = ImageTk.PhotoImage(i)
            self.config(
                image=self.title_image,
            )
            self.pack()


    class VirtualKeyboard(tk.Frame):
        KEYBOARD = [
            [["Q", "q"], ["W", "w"], ["E", "e"], ["R", "r"], ["T", "t"], ["Y", "y"], ["U", "u"], ["I", "i"], ["O", "o"], ["P", "p"]],
            [["A", "a"], ["S", "s"], ["D", "d"], ["F", "f"], ["G", "g"], ["H", "h"], ["J", "j"], ["K", "k"], ["L", "l"]],
            [["Enter", "Return"], ["Z", "z"], ["X", "x"], ["C", "c"], ["V", "v"], ["B", "b"], ["N", "n"], ["M", "m"], ["←", "BackSpace"]]
        ]
        def __init__(self, parent, **kwargs):
            super().__init__(parent, **kwargs)
            self.pack(pady=5)
            self.keyboard_row_frames = [
                tk.Frame(self) for _ in range(len(self.KEYBOARD))
            ]
            self.keys = [[], [], []]
            for i, row in enumerate(self.KEYBOARD):
                self.keyboard_row_frames[i].pack(pady=2)
                for key in row:
                    self.keys[i].append(
                        parent.VirtualKeyboardKey(
                            parent=self.keyboard_row_frames[i],
                            keysym=key[1],
                            text=key[0],
                            width=len(key[0]),
                        )
                    )

        def reset_keys(self):
            for row in self.keys:
                for k in row:
                    k.reset_key()

        def set_key_status(self, key, status):
            for i, row in enumerate(self.keys):
                for j, k in enumerate(row):
                    if k["text"] == key:
                        self.keys[i][j].set_key_status(status)
                        return


    class VirtualKeyboardKey(tk.Button):
        def __init__(self, parent, keysym, **kwargs):
            super().__init__(parent, **kwargs)
            self.config(
                bg=ui.color["init"]["pri"]["bg"],
                fg=ui.color["init"]["pri"]["fg"],
                font=ui.font["keyboard"],
                padx=3,
                cursor="hand2",
            )
            self.keysym = keysym
            self.status = "init"
            self.bind("<Button-1>", lambda e: self.on_click(self.keysym))
            self.bind("<Enter>", lambda e: self.on_hover())
            self.bind("<Leave>", lambda e: self.off_hover())
            self.pack(side="left", padx=2)

        def on_click(self, keysym):
            # simulate physical keyboard key press
            self.event_generate(f"<KeyRelease-{keysym}>")

        def on_hover(self):
            self['bg'] = ui.color[self.status]["sec"]["bg"]
            self['fg'] = ui.color[self.status]["sec"]["fg"]

        def off_hover(self):
            self['bg'] = ui.color[self.status]["pri"]["bg"]
            self['fg'] = ui.color[self.status]["pri"]["fg"]

        def reset_key(self):
            self.status = "init"
            self['bg'] = ui.color["init"]["pri"]["bg"]
            self['fg'] = ui.color["init"]["pri"]["fg"]

        def set_key_status(self, status):
            self.status = status
            self['bg'] = ui.color[status]["pri"]["bg"]
            self['fg'] = ui.color[status]["pri"]["fg"]


    class GameOver(tk.Toplevel):
        def __init__(self, parent):
            super().__init__(parent)
            self._parent = parent
            self._parent.attributes('-disabled', True)
            self.protocol("WM_DELETE_WINDOW", self.close)
            self.focus_force()
            self.wm_iconbitmap('images/icon.ico')
            self.title("Game Over")
            x_co = int(self._parent.width / 2 - (450 / 2)) + self._parent.x_co
            y_co = self._parent.y_co + int(self._parent.height / 2 - (250 / 2))
            self.geometry(f"450x250+{x_co}+{y_co}")

            status = "You Won !!!"
            if not self._parent.won:
                status = "You Lost :("
            status_label = tk.Label(
                self,
                text=status,
                font=ui.font["label2"],
                fg=ui.color["feedback"]["pri"]["fg"],
            )
            status_label.pack(pady=10)

            if not self._parent.won:
                right_word = tk.Label(
                    self,
                    text=f"The word was {self._parent.rules.word}",
                    font=ui.font["label1"],
                    fg=ui.color["feedback"]["pri"]["fg"],
                )
                right_word.pack(pady=4)

            score_label = tk.Label(
                self,
                text=f"Score : {self._parent.score}",
                font=ui.font["label1"],
            )
            score_label.pack(pady=4)

            high_score_label = tk.Label(
                self,
                text=f"High Score : {self._parent.rules.high_score}",
                font=ui.font["label1"],
            )
            high_score_label.pack(pady=4)

            button = tk.Button(
                self,
                text="Okay",
                command=self.close,
                font=ui.font["button"],
                padx=10,
                cursor="hand2",
            )
            button.bind("<Return>", lambda event: button.invoke())
            button.focus_set()
            button.pack(pady=4)

        def close(self):
            self._parent.reset_board(gameover=self)


    class Settings(tk.Toplevel):
        def __init__(self, parent, **kwargs):
            super().__init__(parent, **kwargs)
            self.parent = parent
            self.parent.attributes('-disabled', True)
            self.protocol("WM_DELETE_WINDOW", self.close)
            self.focus_force()
            self.wm_iconbitmap('images/icon.ico')
            self.title("Settings")
            x_co = int(self.parent.width / 2 - (400 / 2)) + self.parent.x_co
            y_co = self.parent.y_co + int(self.parent.height / 2 - (200 / 2))
            self.geometry(f"400x200+{x_co}+{y_co}")

            settings_frame = tk.Frame(self)
            settings_frame.pack(pady=30)

            self.BaseLabel(settings_frame, text="Size").grid(row=0, column=0)
            self.word_length_label = self.ValueLabel(
                settings_frame,
                value=self.parent.rules.word_length,
                min=self.parent.rules.min_word_length,
                max=self.parent.rules.max_word_length,
            )
            self.word_length_label.grid(row=0, column=2)
            decrease_len_btn = self.IncrementButton(settings_frame, self.word_length_label, -1)
            decrease_len_btn.grid(row=0, column=1)
            increase_len_btn = self.IncrementButton(settings_frame, self.word_length_label, +1)
            increase_len_btn.grid(row=0, column=3)

            self.BaseLabel(settings_frame, text="Score").grid(row=1, column=0)
            self.high_score_label = self.ValueLabel(
                settings_frame,
                value=self.parent.rules.high_score,
                min=self.parent.rules.min_high_score,
                max=self.parent.rules.max_high_score,
            )
            self.high_score_label.grid(row=1, column=2)
            decrease_score_btn = self.IncrementButton(settings_frame, self.high_score_label, -1)
            decrease_score_btn.grid(row=1, column=1)
            increase_score_btn = self.IncrementButton(settings_frame, self.high_score_label, +1)
            increase_score_btn.grid(row=1, column=3)

            self.change_settings = self.BaseButton(self, text="Change", command=self.save_changes)
            self.change_settings.pack()

        def save_changes(self):
            self.parent.rules.new_rules(
                word_length=self.word_length_label.value,
                high_score=self.high_score_label.value
            )
            self.parent.reset_rules(settings=self)

        def close(self):
            self.parent.attributes('-disabled', False)
            self.parent.focus_force()
            self.destroy()


        class BaseButton(tk.Button):
            def __init__(self, parent, **kwargs):
                super().__init__(parent, **kwargs)
                self._parent = parent
                self.config(
                    font=ui.font["button"],
                    cursor="hand2",
                )
                self.bind("<Enter>", self.on_hover)
                self.bind("<Leave>", self.off_hover)

            def on_hover(self, event):
                event.widget["bg"] = ui.color["button"]["sec"]["bg"]

            def off_hover(self, event):
                event.widget["bg"] = self._parent["bg"]


        class IncrementButton(BaseButton):
            def __init__(self, parent, label, increment, **kwargs):
                super().__init__(parent, **kwargs)
                self._label = label
                self._increment = increment
                if increment < 0:
                    i = Image.open("images/decrease.png")
                else:
                    i = Image.open("images/increase.png")
                i = i.resize((40, 40), Image.Resampling.LANCZOS)
                i = ImageTk.PhotoImage(i)
                self.image = i
                self.config(
                    image=i,
                    bd=0,
                )
                self.bind("<Button-1>", self.on_click)

            def on_click(self, event):
                self._label.value += self._increment
                if self._label.min is not None:
                    if self._label.value < self._label.min:
                        self._label.value = self._label.min
                if self._label.max is not None:
                    if self._label.value > self._label.max:
                        self._label.value = self._label.max
                self._label["text"] = self._label.value


        class BaseLabel(tk.Label):
            def __init__(self, parent, **kwargs):
                super().__init__(parent, **kwargs)
                self.config(
                    font=ui.font["label1"],
                )


        class ValueLabel(BaseLabel):
            def __init__(self, parent, value, min, max, **kwargs):
                super().__init__(parent, **kwargs)
                self.value = value
                self.min = min
                self.max = max
                self.config(
                    text=self.value,
                )
