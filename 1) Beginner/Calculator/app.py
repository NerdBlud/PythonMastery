import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# ------------------ Main Window ------------------
app = ctk.CTk()
app.title("Calculator")
app.geometry("400x500")
app.resizable(False, False)

# ------------------ Entry Field ------------------
entry = ctk.CTkEntry(app, width=340, height=50, font=("Arial", 24), justify="right")
entry.grid(row=0, column=0, columnspan=4, padx=10, pady=20)

# ------------------ Logic ------------------
def click_button(value):
    entry.insert("end", value)

def clear_entry():
    entry.delete(0, "end")

def calculate():
    try:
        result = eval(entry.get())
        entry.delete(0, "end")
        entry.insert(0, str(result))
    except Exception:
        messagebox.showerror("Error", "Invalid Expression")
        entry.delete(0, "end")

# ------------------ Animated Button Class ------------------
class AnimatedButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_color = self.cget("fg_color")
        self.hover_color = "#FFB347"
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.configure(fg_color=self.hover_color)
        self.after(50, lambda: self.configure(fg_color=self.hover_color))

    def on_leave(self, e):
        self.configure(fg_color=self.default_color)

# ------------------ Buttons ------------------
button_texts = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"]
]

for r, row in enumerate(button_texts, start=1):
    for c, char in enumerate(row):
        if char == "=":
            btn = AnimatedButton(app, text=char, width=80, height=60, corner_radius=10,
                                 fg_color="orange", hover_color="#FFB347", command=calculate)
        else:
            btn = AnimatedButton(app, text=char, width=80, height=60, corner_radius=10,
                                 fg_color="#FFA500", hover_color="#FFB347",
                                 command=lambda val=char: click_button(val))
        btn.grid(row=r, column=c, padx=5, pady=5)

# ------------------ Clear Button ------------------
clear_btn = AnimatedButton(app, text="C", width=340, height=50, corner_radius=10,
                           fg_color="#FF4500", hover_color="#FF6347",
                           command=clear_entry)
clear_btn.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

# ------------------ Run App ------------------
app.mainloop()
