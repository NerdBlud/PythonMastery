from tkinterdnd2 import DND_FILES, TkinterDnD
import customtkinter as ctk
from tkhtmlview import HTMLLabel
from tkinter import filedialog, messagebox
import markdown
from pathlib import Path
import tkinter as tk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

app = TkinterDnD.Tk()
app.title(" Markdown Studio")
app.geometry("1200x700")

md_files=[]
CSS_PATH=Path("css/neon.css")

def hover(widget,color,orig):
    widget.bind("<Enter>",lambda e:widget.configure(fg_color=color))
    widget.bind("<Leave>",lambda e:widget.configure(fg_color=orig))

title=ctk.CTkLabel(app,text=" Markdown Studio",font=("Orbitron",32,"bold"),text_color="#ff80ff")
title.pack(pady=20)

frame_files=ctk.CTkFrame(app,fg_color="#2c2c3f",corner_radius=20,border_width=2,border_color="#8000ff")
frame_files.pack(pady=10,padx=20,fill="x")

def browse():
    files=filedialog.askopenfilenames(filetypes=[("Markdown files","*.md")])
    if files:
        md_files.clear()
        md_files.extend(files)
        md_list.delete("1.0","end")
        for f in md_files: md_list.insert("end",f+"\n")

btn_browse=ctk.CTkButton(frame_files,text="Browse Markdown Files",fg_color="#800080",hover_color="#a64ca6",command=browse)
btn_browse.pack(side="left",padx=10,pady=10)
hover(btn_browse,"#a64ca6","#800080")

md_list=ctk.CTkTextbox(frame_files,width=700,height=60,corner_radius=10,fg_color="#1e1e2f",text_color="#ff80ff",font=("Orbitron",12))
md_list.pack(side="left",padx=10,pady=10)

pw=tk.PanedWindow(app,orient="horizontal",sashrelief="raised",bg="#1e1e2f")
pw.pack(fill="both",expand=True,padx=20,pady=20)

md_frame=ctk.CTkFrame(pw,fg_color="#2c2c3f",corner_radius=20)
md_text=ctk.CTkTextbox(md_frame,fg_color="#1e1e2f",text_color="#fff",font=("Courier",14))
md_text.pack(fill="both",expand=True,padx=10,pady=10)
pw.add(md_frame)

html_frame=ctk.CTkFrame(pw,fg_color="#2c2c3f",corner_radius=20)
html_preview=HTMLLabel(html_frame,html="",background="#1e1e2f")
html_preview.pack(fill="both",expand=True,padx=10,pady=10)
pw.add(html_frame)

def update_preview():
    md_content=md_text.get("1.0","end")
    html=markdown.markdown(md_content,extensions=["fenced_code","codehilite"])
    if CSS_PATH.exists():
        with open(CSS_PATH,"r") as f: html=f"<style>{f.read()}</style>"+html
    html_preview.set_html(html)

btn_preview=ctk.CTkButton(app,text="Live Preview",fg_color="#800080",hover_color="#a64ca6",command=update_preview,font=("Orbitron",14,"bold"))
btn_preview.pack(pady=10)
hover(btn_preview,"#a64ca6","#800080")

def batch_convert():
    if not md_files:
        messagebox.showwarning("Warning","No Markdown files selected!")
        return
    for md_file in md_files:
        path=Path(md_file)
        content=path.read_text(encoding="utf-8")
        html=markdown.markdown(content,extensions=["fenced_code","codehilite"])
        if CSS_PATH.exists():
            with open(CSS_PATH,"r") as f: html=f"<style>{f.read()}</style>"+html
        save_path=filedialog.asksaveasfilename(initialfile=path.stem+".html",defaultextension=".html",filetypes=[("HTML files","*.html")])
        if save_path: Path(save_path).write_text(html,encoding="utf-8")
    messagebox.showinfo("Success","Batch conversion complete!")

btn_batch=ctk.CTkButton(app,text="Convert & Save Batch",fg_color="#800080",hover_color="#a64ca6",command=batch_convert,font=("Orbitron",14,"bold"))
btn_batch.pack(pady=10)
hover(btn_batch,"#a64ca6","#800080")

def drop(event):
    files=app.tk.splitlist(event.data)
    for f in files:
        if f.endswith(".md"):
            md_files.append(f)
            md_list.insert("end",f+"\n")

md_list.drop_target_register(DND_FILES)
md_list.dnd_bind('<<Drop>>',drop)

app.mainloop()
