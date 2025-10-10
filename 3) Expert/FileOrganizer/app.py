import os
import shutil
from pathlib import Path
from datetime import datetime
import json
import hashlib
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox, BooleanVar, Checkbutton, Text, Scrollbar, END

# ------------------ Config ------------------
DEFAULT_FILE_TYPES = {
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Audio": [".mp3", ".wav", ".flac"],
    "Archives": [".zip", ".rar", ".tar", ".gz"]
}

UNDO_FOLDER = ".file_organizer_undo"
CUSTOM_CATEGORIES_FILE = "custom_categories.json"

# ------------------ Category Handling ------------------
def load_custom_categories():
    if os.path.exists(CUSTOM_CATEGORIES_FILE):
        with open(CUSTOM_CATEGORIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_FILE_TYPES.copy()

def save_custom_categories(categories_dict):
    with open(CUSTOM_CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(categories_dict, f, indent=2)

# ------------------ Core Functions ------------------
def get_file_hash(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def organize_folder(folder_path, by_date=False, custom_rules=None, safe_mode=False, log_list=None):
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Folder {folder_path} does not exist or is not a directory.")

    moved_files = []
    hashes_seen = set()
    file_types = custom_rules if custom_rules else DEFAULT_FILE_TYPES

    for file in folder.iterdir():
        if file.is_file():
            file_hash = get_file_hash(file)
            if file_hash in hashes_seen:
                target_folder = folder / "Duplicates"
            else:
                hashes_seen.add(file_hash)
                target_folder = None
                for category, extensions in file_types.items():
                    if file.suffix.lower() in extensions:
                        target_folder = folder / category
                        break
                if not target_folder:
                    target_folder = folder / "Others"

                if by_date:
                    modified_time = datetime.fromtimestamp(file.stat().st_mtime)
                    target_folder = target_folder / str(modified_time.year) / f"{modified_time.month:02}"

            target_folder.mkdir(parents=True, exist_ok=True)
            dest = target_folder / file.name

            if safe_mode:
                moved_files.append({"src": str(file), "dest": str(dest)})
            else:
                shutil.move(str(file), str(dest))
                moved_files.append({"src": str(file), "dest": str(dest)})
                if log_list is not None:
                    log_list.append(f"{file} -> {dest}")

    if moved_files and not safe_mode:
        undo_path = folder / UNDO_FOLDER
        undo_path.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(undo_path / f"undo_{timestamp}.json", "w", encoding="utf-8") as f:
            json.dump(moved_files, f, indent=2)

    return moved_files

def undo_last(folder_path):
    folder = Path(folder_path)
    undo_path = folder / UNDO_FOLDER
    if not undo_path.exists():
        print("No undo history found.")
        return

    undo_files = sorted(undo_path.glob("undo_*.json"), reverse=True)
    if not undo_files:
        print("No undo snapshots found.")
        return

    latest = undo_files[0]
    with open(latest, "r", encoding="utf-8") as f:
        moved_files = json.load(f)

    for item in reversed(moved_files):
        src = Path(item["dest"])
        dest = Path(item["src"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            shutil.move(str(src), str(dest))

    latest.unlink()
    print(f"Reverted {len(moved_files)} files from last operation.")

def batch_organize(folders, by_date=False, custom_rules=None, safe_mode=False, log_list=None):
    all_moved = []
    for folder in folders:
        moved = organize_folder(folder, by_date, custom_rules, safe_mode, log_list)
        all_moved.extend(moved)
    return all_moved

# ------------------ GUI: Category Editor ------------------
def edit_categories_gui(parent):
    categories = load_custom_categories()

    editor = tk.Toplevel(parent)
    editor.title("Custom Categories Editor")
    editor.geometry("400x400")

    tk.Label(editor, text="Category Name").grid(row=0, column=0, padx=5, pady=5)
    tk.Label(editor, text="Extensions (comma-separated)").grid(row=0, column=1, padx=5, pady=5)

    entries = {}
    for i, (cat, exts) in enumerate(categories.items(), start=1):
        cat_var = tk.StringVar(value=cat)
        exts_var = tk.StringVar(value=",".join(exts))
        tk.Entry(editor, textvariable=cat_var).grid(row=i, column=0, padx=5, pady=2)
        tk.Entry(editor, textvariable=exts_var).grid(row=i, column=1, padx=5, pady=2)
        entries[i] = (cat_var, exts_var)

    def save_categories():
        new_categories = {}
        for cat_var, exts_var in entries.values():
            name = cat_var.get().strip()
            exts = [e.strip() if e.startswith('.') else '.'+e.strip() for e in exts_var.get().split(',') if e.strip()]
            if name and exts:
                new_categories[name] = exts
        save_custom_categories(new_categories)
        messagebox.showinfo("Saved", "Custom categories saved successfully!")
        editor.destroy()

    tk.Button(editor, text="Save", command=save_categories).grid(row=i+1, column=0, columnspan=2, pady=10)

# ------------------ GUI: Main ------------------
def run_gui():
    root = tk.Tk()
    root.title("File Organizer Pro")
    root.geometry("600x400")

    folder_paths = []
    log_text = Text(root, height=10)
    log_text.pack(side="bottom", fill="both", expand=True)
    scrollbar = Scrollbar(root, command=log_text.yview)
    scrollbar.pack(side="right", fill="y")
    log_text.config(yscrollcommand=scrollbar.set)

    by_date_var = BooleanVar(value=False)
    safe_mode_var = BooleanVar(value=False)

    def select_folder():
        folders = filedialog.askdirectory(mustexist=True)
        if folders:
            folder_paths.clear()
            folder_paths.append(folders)
            folder_label.config(text=folders)

    def start_organize():
        if not folder_paths:
            messagebox.showwarning("Warning", "Select folder first!")
            return
        log_entries = []
        custom_rules = load_custom_categories()
        moved = batch_organize(folder_paths, by_date_var.get(), custom_rules, safe_mode_var.get(), log_list=log_entries)
        for entry in log_entries:
            log_text.insert(END, entry + "\n")
        messagebox.showinfo("Done", f"Organized {len(moved)} files.")

    def start_undo():
        if not folder_paths:
            messagebox.showwarning("Warning", "Select folder first!")
            return
        for folder in folder_paths:
            undo_last(folder)
        messagebox.showinfo("Done", "Undo completed!")

    tk.Button(root, text="Select Folder", command=select_folder).pack(pady=5)
    folder_label = tk.Label(root, text="No folder selected")
    folder_label.pack()
    Checkbutton(root, text="Organize by Date", variable=by_date_var).pack()
    Checkbutton(root, text="Safe/Preview Mode", variable=safe_mode_var).pack()
    tk.Button(root, text="Edit Categories", command=lambda: edit_categories_gui(root)).pack(pady=5)
    tk.Button(root, text="Organize", command=start_organize).pack(pady=5)
    tk.Button(root, text="Undo Last", command=start_undo).pack(pady=5)

    root.mainloop()

# ------------------ CLI ------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File Organizer Pro Full")
    parser.add_argument("--folders", nargs="+", help="Folders to organize")
    parser.add_argument("--by-date", action="store_true", help="Organize by modification date")
    parser.add_argument("--undo", action="store_true", help="Undo last operation")
    parser.add_argument("--safe", action="store_true", help="Preview mode, no files moved")
    args = parser.parse_args()

    if args.folders:
        if args.undo:
            for f in args.folders:
                undo_last(f)
        else:
            custom_rules = load_custom_categories()
            moved = batch_organize(args.folders, args.by_date, custom_rules, safe_mode=args.safe)
            print(f"Organized {len(moved)} files across {len(args.folders)} folder(s).")
    else:
        run_gui()
