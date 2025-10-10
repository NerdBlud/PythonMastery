import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ------------------ Main Window ------------------
app = ctk.CTk()
app.title("Quiz Game")
app.geometry("500x400")
app.resizable(False, False)

# ------------------ Quiz Data ------------------
QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Rome"],
        "answer": "Paris"
    },
    {
        "question": "Which language is this program written in?",
        "options": ["Python", "Java", "C++", "Ruby"],
        "answer": "Python"
    },
    {
        "question": "What is 5 * 6?",
        "options": ["11", "30", "56", "28"],
        "answer": "30"
    },
    {
        "question": "What is the chemical symbol for water?",
        "options": ["O2", "H2O", "CO2", "HO"],
        "answer": "H2O"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "answer": "Mars"
    },
]

# ------------------ Game Logic ------------------
class QuizGame:
    def __init__(self):
        self.score = 0
        self.current_question = 0
        self.load_question()

    def load_question(self):
        if self.current_question < len(QUESTIONS):
            q = QUESTIONS[self.current_question]
            question_label.configure(text=q["question"])
            for i, option in enumerate(q["options"]):
                option_buttons[i].configure(text=option)
        else:
            messagebox.showinfo("Quiz Finished", f"Your final score: {self.score}/{len(QUESTIONS)}")
            self.reset_game()

    def check_answer(self, idx):
        selected = option_buttons[idx].cget("text")
        correct = QUESTIONS[self.current_question]["answer"]
        if selected == correct:
            self.score += 1
            feedback_label.configure(text="✅ Correct!", text_color="green")
        else:
            feedback_label.configure(text=f"❌ Wrong! Correct: {correct}", text_color="red")
        self.current_question += 1
        app.after(1000, self.load_question)

    def reset_game(self):
        self.score = 0
        self.current_question = 0
        feedback_label.configure(text="")
        self.load_question()

# ------------------ UI Elements ------------------
question_label = ctk.CTkLabel(app, text="", font=("Arial", 18), wraplength=450)
question_label.pack(pady=20)

option_buttons = []
for i in range(4):
    btn = ctk.CTkButton(app, text="", width=300, height=50, corner_radius=10)
    btn.pack(pady=5)
    option_buttons.append(btn)

feedback_label = ctk.CTkLabel(app, text="", font=("Arial", 16))
feedback_label.pack(pady=10)

restart_btn = ctk.CTkButton(app, text="Restart Quiz", width=150, height=40, corner_radius=10)
restart_btn.pack(pady=10)

# ------------------ Hover Effect Function ------------------
def hover_effect(widget, color, original_color):
    def on_enter(e): widget.configure(fg_color=color)
    def on_leave(e): widget.configure(fg_color=original_color)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

hover_effect(restart_btn, "#FF6347", "#FF4500")
for btn in option_buttons:
    hover_effect(btn, "#FFA500", "#FFA07A")

# ------------------ Initialize Game ------------------
game = QuizGame()

for idx, btn in enumerate(option_buttons):
    btn.configure(command=lambda i=idx: game.check_answer(i))

restart_btn.configure(command=game.reset_game)

# ------------------ Run App ------------------
app.mainloop()
