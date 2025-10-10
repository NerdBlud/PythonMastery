import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Image Watermark App")
app.geometry("1000x700")

original_image = None
display_image = None
watermark_image = None

def load_image():
    global original_image, display_image
    path = filedialog.askopenfilename(filetypes=[("Image files","*.png;*.jpg;*.jpeg")])
    if path:
        original_image = Image.open(path).convert("RGBA")
        display_image = original_image.copy()
        update_canvas(display_image)

def load_watermark_image():
    global watermark_image
    path = filedialog.askopenfilename(filetypes=[("Image files","*.png;*.jpg;*.jpeg")])
    if path:
        watermark_image = Image.open(path).convert("RGBA")
        update_watermark()

def update_canvas(img):
    img_copy = img.copy()
    img_copy.thumbnail((700, 600))
    tk_img = ImageTk.PhotoImage(img_copy)
    canvas.image = tk_img
    canvas.create_image(0,0, anchor="nw", image=tk_img)

def update_watermark(*args):
    global display_image
    if original_image:
        display_image = original_image.copy()
        txt = text_var.get()
        opacity = int(opacity_scale.get())
        font_size = int(size_scale.get())
        font_name = font_var.get()
        try:
            font = ImageFont.truetype(font_name, font_size)
        except:
            font = ImageFont.load_default()
        txt_layer = Image.new("RGBA", display_image.size, (0,0,0,0))
        draw = ImageDraw.Draw(txt_layer)
        draw.text((int(pos_x.get()), int(pos_y.get())), txt, font=font, fill=(255,255,255,opacity))
        display_image = Image.alpha_composite(display_image, txt_layer)
        if watermark_image:
            wm = watermark_image.copy()
            wm = wm.resize((int(wm.width*wm_scale.get()/100), int(wm.height*wm_scale.get()/100)))
            mask = wm.split()[3].point(lambda i: i*opacity/255)
            display_image.paste(wm, (int(pos_x_img.get()), int(pos_y_img.get())), mask)
        update_canvas(display_image)

def save_image():
    if display_image:
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG","*.png"),("JPEG","*.jpg")])
        if path:
            display_image.convert("RGB").save(path)

main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

canvas_frame = ctk.CTkFrame(main_frame)
canvas_frame.pack(side="left", fill="both", expand=True, padx=(0,10))
controls_frame = ctk.CTkFrame(main_frame, width=300)
controls_frame.pack(side="right", fill="y")

canvas = ctk.CTkCanvas(canvas_frame, width=700, height=600, bg="#333333")
canvas.pack(pady=10)

ctk.CTkButton(controls_frame, text="Load Image", command=load_image).pack(pady=5, fill="x")
ctk.CTkButton(controls_frame, text="Load Watermark Image", command=load_watermark_image).pack(pady=5, fill="x")

text_var = ctk.StringVar(value="Your Watermark")
text_entry = ctk.CTkEntry(controls_frame, textvariable=text_var, placeholder_text="Watermark Text")
text_entry.pack(pady=5, fill="x")
text_var.trace_add("write", update_watermark)

font_var = ctk.StringVar(value="arial.ttf")
font_entry = ctk.CTkEntry(controls_frame, textvariable=font_var, placeholder_text="Font (e.g. arial.ttf)")
font_entry.pack(pady=5, fill="x")
font_var.trace_add("write", update_watermark)

ctk.CTkLabel(controls_frame, text="Text X Position").pack(pady=(10,0))
pos_x = ctk.CTkSlider(controls_frame, from_=0, to=800, command=lambda e=None:update_watermark())
pos_x.pack(fill="x")

ctk.CTkLabel(controls_frame, text="Text Y Position").pack(pady=(10,0))
pos_y = ctk.CTkSlider(controls_frame, from_=0, to=600, command=lambda e=None:update_watermark())
pos_y.pack(fill="x")

ctk.CTkLabel(controls_frame, text="Font Size").pack(pady=(10,0))
size_scale = ctk.CTkSlider(controls_frame, from_=10, to=200, command=lambda e=None:update_watermark())
size_scale.set(50)
size_scale.pack(fill="x")

ctk.CTkLabel(controls_frame, text="Opacity").pack(pady=(10,0))
opacity_scale = ctk.CTkSlider(controls_frame, from_=0, to=255, command=lambda e=None:update_watermark())
opacity_scale.set(128)
opacity_scale.pack(fill="x")

ctk.CTkLabel(controls_frame, text="Image Watermark Scale (%)").pack(pady=(10,0))
wm_scale = ctk.CTkSlider(controls_frame, from_=10, to=200, command=lambda e=None:update_watermark())
wm_scale.set(50)
wm_scale.pack(fill="x")

ctk.CTkLabel(controls_frame, text="Image Watermark X").pack(pady=(10,0))
pos_x_img = ctk.CTkSlider(controls_frame, from_=0, to=800, command=lambda e=None:update_watermark())
pos_x_img.pack(fill="x")

ctk.CTkLabel(controls_frame, text="Image Watermark Y").pack(pady=(10,0))
pos_y_img = ctk.CTkSlider(controls_frame, from_=0, to=600, command=lambda e=None:update_watermark())
pos_y_img.pack(fill="x")

ctk.CTkButton(controls_frame, text="Save Image", command=save_image).pack(pady=10, fill="x")

app.mainloop()
