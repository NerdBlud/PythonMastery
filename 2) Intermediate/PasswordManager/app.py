import customtkinter as ctk
from tkinter import messagebox, simpledialog
from cryptography.fernet import Fernet
import json
from pathlib import Path
import hashlib
import string
import random

# ------------------ Config ------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

DATA_FILE = Path("passwords.json")
KEY_FILE = Path("secret.key")
MASTER_FILE = Path("master.key")

# ------------------ Generate or load key ------------------
def load_key():
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    return key

KEY = load_key()
fernet = Fernet(KEY)

# ------------------ Master Password ------------------
def check_master():
    if not MASTER_FILE.exists():
        pw = simpledialog.askstring("Master Password", "Set a master password:", show="*")
        if pw:
            hash_pw = hashlib.sha256(pw.encode()).hexdigest()
            MASTER_FILE.write_text(hash_pw)
        else:
            messagebox.showerror("Error", "Master password required!")
            exit()
    else:
        while True:
            pw = simpledialog.askstring("Master Password", "Enter master password:", show="*")
            hash_pw = hashlib.sha256(pw.encode()).hexdigest()
            if hash_pw == MASTER_FILE.read_text():
                break
            else:
                messagebox.showerror("Error", "Incorrect password!")

check_master()

# ------------------ Load/Save passwords ------------------
def load_passwords():
    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text())
        for account in data:
            data[account] = fernet.decrypt(data[account].encode()).decode()
        return data
    return {}

def save_passwords(data):
    enc_data = {acc: fernet.encrypt(pw.encode()).decode() for acc, pw in data.items()}
    DATA_FILE.write_text(json.dumps(enc_data, indent=2))

passwords = load_passwords()

# ------------------ App Setup ------------------
app = ctk.CTk()
app.title("Password Manager")
app.geometry("600x600")
app.resizable(False, False)

# ------------------ Hover Effect ------------------
def hover_effect(widget, color, original_color):
    def on_enter(e): widget.configure(fg_color=color)
    def on_leave(e): widget.configure(fg_color=original_color)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

# ------------------ UI Elements ------------------
title_label = ctk.CTkLabel(app, text="Password Manager", font=("Arial", 24))
title_label.pack(pady=20)

search_entry = ctk.CTkEntry(app, width=400, placeholder_text="Search account...")
search_entry.pack(pady=5)

account_entry = ctk.CTkEntry(app, width=400, placeholder_text="Account (e.g., Gmail)")
account_entry.pack(pady=10)

password_entry = ctk.CTkEntry(app, width=400, placeholder_text="Password", show="*")
password_entry.pack(pady=10)

display_frame = ctk.CTkFrame(app, width=550, height=300)
display_frame.pack(pady=15)
display_frame.pack_propagate(False)

# ------------------ Password Generation ------------------
def generate_password(length=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def add_generated_password():
    password_entry.delete(0, "end")
    password_entry.insert(0, generate_password())

# ------------------ Clipboard ------------------
def copy_to_clipboard(pw):
    app.clipboard_clear()
    app.clipboard_append(pw)
    messagebox.showinfo("Copied", "Password copied to clipboard")

# ------------------ Task Management ------------------
def add_task_widget(idx, acc, pw):
    container = ctk.CTkFrame(display_frame, fg_color="#1e1e2f", corner_radius=10)
    container.pack(pady=5, padx=5, fill="x")
    
    label = ctk.CTkLabel(container, text=f"{acc}: {pw}", font=("Arial", 14), anchor="w")
    label.pack(side="left", padx=10, pady=10, expand=True, fill="x")
    
    copy_btn = ctk.CTkButton(container, text="📋", width=40, fg_color="#800080", hover_color="#a64ca6",
                             command=lambda p=pw: copy_to_clipboard(p))
    copy_btn.pack(side="right", padx=5)
    hover_effect(copy_btn, "#a64ca6", "#800080")
    
    edit_btn = ctk.CTkButton(container, text="✏️", width=40, fg_color="#800080", hover_color="#a64ca6",
                             command=lambda i=idx: edit_password(i))
    edit_btn.pack(side="right", padx=5)
    hover_effect(edit_btn, "#a64ca6", "#800080")
    
    del_btn = ctk.CTkButton(container, text="❌", width=40, fg_color="#800080", hover_color="#a64ca6",
                            command=lambda i=idx: delete_password(i))
    del_btn.pack(side="right", padx=5)
    hover_effect(del_btn, "#a64ca6", "#800080")

def refresh_display():
    for widget in display_frame.winfo_children():
        widget.destroy()
    query = search_entry.get().strip().lower()
    for i, (acc, pw) in enumerate(passwords.items()):
        if query in acc.lower():
            add_task_widget(i, acc, pw)

def add_password():
    acc = account_entry.get().strip()
    pw = password_entry.get().strip()
    if acc and pw:
        passwords[acc] = pw
        save_passwords(passwords)
        refresh_display()
        account_entry.delete(0, "end")
        password_entry.delete(0, "end")
    else:
        messagebox.showwarning("Warning", "Account and password cannot be empty")

def delete_password(idx):
    acc = list(passwords.keys())[idx]
    if messagebox.askyesno("Delete", f"Delete password for {acc}?"):
        passwords.pop(acc)
        save_passwords(passwords)
        refresh_display()

def edit_password(idx):
    acc = list(passwords.keys())[idx]
    new_pw = password_entry.get().strip()
    if new_pw:
        passwords[acc] = new_pw
        save_passwords(passwords)
        refresh_display()
        password_entry.delete(0, "end")
    else:
        messagebox.showwarning("Warning", "Password cannot be empty")

def filter_passwords(*args):
    refresh_display()

search_entry.bind("<KeyRelease>", filter_passwords)

# ------------------ Buttons ------------------
btn_frame = ctk.CTkFrame(app, fg_color="#1e1e2f")
btn_frame.pack(pady=10)

add_btn = ctk.CTkButton(btn_frame, text="Add Password", width=150, fg_color="#800080", hover_color="#a64ca6",
                        command=add_password)
add_btn.pack(side="left", padx=10)
hover_effect(add_btn, "#a64ca6", "#800080")

gen_btn = ctk.CTkButton(btn_frame, text="Generate", width=120, fg_color="#800080", hover_color="#a64ca6",
                        command=add_generated_password)
gen_btn.pack(side="left", padx=10)
hover_effect(gen_btn, "#a64ca6", "#800080")

refresh_btn = ctk.CTkButton(btn_frame, text="Refresh", width=120, fg_color="#800080", hover_color="#a64ca6",
                            command=refresh_display)
refresh_btn.pack(side="left", padx=10)
hover_effect(refresh_btn, "#a64ca6", "#800080")

# ------------------ Initial Load ------------------
refresh_display()

# ------------------ Run App ------------------
app.mainloop()
