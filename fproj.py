import tkinter as tk
from tkinter import messagebox
import random
import json

class Game2048:
    def __init__(self, master):
        self.master = master
        self.master.title("2048")
        self.master.geometry("400x500")
        self.master.resizable(False, False)

        self.colors = {
            0: "#cdc1b4",
            2: "#eee4da",
            4: "#ede0c8",
            8: "#f2b179",
            16: "#f59563",
            32: "#f67c5f",
            64: "#f65e3b",
            128: "#edcf72",
            256: "#edcc61",
            512: "#edc850",
            1024: "#edc53f",
            2048: "#edc22e"
        }

        self.score = 0
        self.high_score = self.load_high_score()
        self.grid = [[0] * 4 for _ in range(4)]
        self.undo_stack = []

        self.create_widgets()
        self.new_game()

    def create_widgets(self):
        self.score_frame = tk.Frame(self.master)
        self.score_frame.pack(pady=10)

        self.score_label = tk.Label(self.score_frame, text="Score: 0", font=("Arial", 14))
        self.score_label.pack(side=tk.LEFT, padx=10)

        self.high_score_label = tk.Label(self.score_frame, text=f"High Score: {self.high_score}", font=("Arial", 14))
        self.high_score_label.pack(side=tk.LEFT, padx=10)

        self.grid_frame = tk.Frame(self.master, bg="#bbada0")
        self.grid_frame.pack(padx=10, pady=10)

        self.cells = []
        for i in range(4):
            row = []
            for j in range(4):
                cell = tk.Label(self.grid_frame, width=6, height=3, font=("Arial", 20, "bold"), bg=self.colors[0])
                cell.grid(row=i, column=j, padx=5, pady=5)
                row.append(cell)
            self.cells.append(row)

        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(pady=10)

        self.new_game_button = tk.Button(self.button_frame, text="New Game", command=self.new_game)
        self.new_game_button.pack(side=tk.LEFT, padx=5)

        self.undo_button = tk.Button(self.button_frame, text="Undo", command=self.undo_move)
        self.undo_button.pack(side=tk.LEFT, padx=5)

        self.master.bind("<Key>", self.key_press)

    def new_game(self):
        self.score = 0
        self.update_score()
        self.grid = [[0] * 4 for _ in range(4)]
        self.undo_stack = []
        self.add_new_tile()
        self.add_new_tile()
        self.update_grid()

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4

    def update_grid(self):
        for i in range(4):
            for j in range(4):
                value = self.grid[i][j]
                self.cells[i][j].config(text=str(value) if value else "", bg=self.colors.get(value, self.colors[2048]))

    def move(self, direction):
        self.undo_stack.append([row[:] for row in self.grid])
        moved = False

        if direction in ("Left", "Right"):
            for i in range(4):
                line = self.grid[i]
                if direction == "Right":
                    line.reverse()
                moved |= self.merge_line(line)
                if direction == "Right":
                    line.reverse()
                self.grid[i] = line
        else:  # Up or Down
            for j in range(4):
                line = [self.grid[i][j] for i in range(4)]
                if direction == "Down":
                    line.reverse()
                moved |= self.merge_line(line)
                if direction == "Down":
                    line.reverse()
                for i in range(4):
                    self.grid[i][j] = line[i]

        if moved:
            self.add_new_tile()
            self.update_grid()
            self.update_score()
            if self.is_game_over():
                self.game_over()
        else:
            self.undo_stack.pop()

    def merge_line(self, line):
        def compress(lst):
            return [x for x in lst if x != 0]

        moved = False
        original = line[:]
        line[:] = compress(line)
        if line != original:
            moved = True

        for i in range(len(line) - 1):
            if line[i] == line[i + 1]:
                line[i] *= 2
                self.score += line[i]
                line[i + 1] = 0
                moved = True

        line[:] = compress(line)
        while len(line) < 4:
            line.append(0)

        return moved

    def key_press(self, event):
        key = event.keysym
        if key in ("Left", "Right", "Up", "Down"):
            self.move(key)

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")
        if self.score > self.high_score:
            self.high_score = self.score
            self.high_score_label.config(text=f"High Score: {self.high_score}")
            self.save_high_score()

    def is_game_over(self):
        if any(0 in row for row in self.grid):
            return False
        for i in range(4):
            for j in range(4):
                if j < 3 and self.grid[i][j] == self.grid[i][j + 1]:
                    return False
                if i < 3 and self.grid[i][j] == self.grid[i + 1][j]:
                    return False
        return True

    def game_over(self):
        messagebox.showinfo("Game Over", f"Game Over! Your score: {self.score}")

    def undo_move(self):
        if self.undo_stack:
            self.grid = self.undo_stack.pop()
            self.update_grid()
            self.score = sum(sum(row) for row in self.grid)
            self.update_score()

    def load_high_score(self):
        try:
            with open("high_score.json", "r") as f:
                return json.load(f)["high_score"]
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def save_high_score(self):
        with open("high_score.json", "w") as f:
            json.dump({"high_score": self.high_score}, f)

if __name__ == "__main__":
    root = tk.Tk()
    game = Game2048(root)
    root.mainloop()
