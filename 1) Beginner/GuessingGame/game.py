import random
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ------------------ Main Window ------------------
app = ctk.CTk()
app.title("Number Guessing Game")
app.geometry("400x300")
app.resizable(False, False)

# ------------------ Game Logic ------------------
class GuessingGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.number = random.randint(1, 100)
        self.attempts = 0

    def check_guess(self):
        try:
            guess = int(entry.get())
            self.attempts += 1
            if guess < self.number:
                feedback_label.configure(text="⬆ Too low!")
            elif guess > self.number:
                feedback_label.configure(text="⬇ Too high!")
            else:
                messagebox.showinfo("🎉 Correct!", f"You guessed it in {self.attempts} attempts!")
                self.reset_game()
                feedback_label.configure(text="")
            entry.delete(0, "end")
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid integer")
            entry.delete(0, "end")

game = GuessingGame()

# ------------------ UI Elements ------------------
title_label = ctk.CTkLabel(app, text="Guess the Number (1-100)", font=("Arial", 18))
title_label.pack(pady=15)

entry = ctk.CTkEntry(app, width=200, font=("Arial", 16))
entry.pack(pady=10)

def hover_effect(widget, color, original_color):
    def on_enter(e): widget.configure(fg_color=color)
    def on_leave(e): widget.configure(fg_color=original_color)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

submit_btn = ctk.CTkButton(app, text="Submit Guess", width=150, height=50, fg_color="#FFA500",
                           corner_radius=10, command=game.check_guess)
submit_btn.pack(pady=10)
hover_effect(submit_btn, "#FFB347", "#FFA500")

feedback_label = ctk.CTkLabel(app, text="", font=("Arial", 16))
feedback_label.pack(pady=10)

restart_btn = ctk.CTkButton(app, text="Restart Game", width=150, height=40, fg_color="#FF4500",
                            corner_radius=10, command=lambda: [game.reset_game(), feedback_label.configure(text="")])
restart_btn.pack(pady=5)
hover_effect(restart_btn, "#FF6347", "#FF4500")

# ------------------ Run App ------------------
app.mainloop()
