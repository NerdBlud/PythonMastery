import customtkinter as ctk
from tkinter import messagebox
import json
from pathlib import Path

# ------------------ Config ------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

DATA_FILE = Path("tasks.json")

# ------------------ Helper Functions ------------------
def load_tasks():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []

def save_tasks(tasks):
    DATA_FILE.write_text(json.dumps(tasks, indent=2))

# ------------------ App Setup ------------------
app = ctk.CTk()
app.title("Professional To-Do List")
app.geometry("500x600")
app.resizable(False, False)

tasks = load_tasks()

# ------------------ Hover Effect ------------------
def hover_effect(widget, color, original_color):
    def on_enter(e): widget.configure(fg_color=color)
    def on_leave(e): widget.configure(fg_color=original_color)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

# ------------------ UI Elements ------------------
title_label = ctk.CTkLabel(app, text="My To-Do List", font=("Arial", 24))
title_label.pack(pady=20)

entry = ctk.CTkEntry(app, width=350, height=40, placeholder_text="Enter a new task...")
entry.pack(pady=10)

task_frame = ctk.CTkFrame(app, width=450, height=400)
task_frame.pack(pady=10)
task_frame.pack_propagate(False)

# ------------------ Task Management ------------------
def refresh_tasks():
    for widget in task_frame.winfo_children():
        widget.destroy()

    for i, task in enumerate(tasks):
        task_container = ctk.CTkFrame(task_frame, fg_color="#1e1e2f", corner_radius=10)
        task_container.pack(pady=5, padx=5, fill="x")

        task_label = ctk.CTkLabel(task_container, text=task, font=("Arial", 16), anchor="w")
        task_label.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        del_btn = ctk.CTkButton(task_container, text="❌", width=40, fg_color="#800080", hover_color="#a64ca6",
                                command=lambda i=i: delete_task(i))
        del_btn.pack(side="right", padx=5, pady=5)
        hover_effect(del_btn, "#a64ca6", "#800080")

        edit_btn = ctk.CTkButton(task_container, text="✏️", width=40, fg_color="#800080", hover_color="#a64ca6",
                                 command=lambda i=i: edit_task(i))
        edit_btn.pack(side="right", padx=5, pady=5)
        hover_effect(edit_btn, "#a64ca6", "#800080")

def add_task():
    task = entry.get().strip()
    if task:
        tasks.append(task)
        save_tasks(tasks)
        refresh_tasks()
        entry.delete(0, "end")
    else:
        messagebox.showwarning("Warning", "Task cannot be empty")

def delete_task(idx):
    tasks.pop(idx)
    save_tasks(tasks)
    refresh_tasks()

def edit_task(idx):
    new_task = entry.get().strip()
    if new_task:
        tasks[idx] = new_task
        save_tasks(tasks)
        refresh_tasks()
        entry.delete(0, "end")
    else:
        messagebox.showwarning("Warning", "Task cannot be empty")

# ------------------ Buttons ------------------
btn_frame = ctk.CTkFrame(app, fg_color="#1e1e2f")
btn_frame.pack(pady=10)

add_btn = ctk.CTkButton(btn_frame, text="Add Task", width=120, fg_color="#800080", hover_color="#a64ca6", command=add_task)
add_btn.pack(side="left", padx=10)
hover_effect(add_btn, "#a64ca6", "#800080")

refresh_btn = ctk.CTkButton(btn_frame, text="Refresh", width=120, fg_color="#800080", hover_color="#a64ca6", command=refresh_tasks)
refresh_btn.pack(side="left", padx=10)
hover_effect(refresh_btn, "#a64ca6", "#800080")

# ------------------ Initial Load ------------------
refresh_tasks()

# ------------------ Run App ------------------
app.mainloop()
