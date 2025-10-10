import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

API_KEY = "api-key"  # i aint putting my api key here boi.. 
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# ------------------ Main Window ------------------
app = ctk.CTk()
app.title("Weather App")
app.geometry("400x500")
app.resizable(False, False)

# ------------------ Cities ------------------
cities = ["Baku", "London", "New York"]

# ------------------ Weather Fetch ------------------
def get_weather(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()

# ------------------ Display ------------------
def show_weather(city):
    try:
        data = get_weather(city)
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].title()
        icon_code = data["weather"][0]["icon"]

        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        icon_response = requests.get(icon_url)
        icon_image = Image.open(BytesIO(icon_response.content))
        icon_image = icon_image.resize((100, 100))
        icon_photo = ImageTk.PhotoImage(icon_image)

        weather_icon.configure(image=icon_photo)
        weather_icon.image = icon_photo
        city_label.configure(text=city)
        temp_label.configure(text=f"{temp}°C")
        desc_label.configure(text=desc)

    except requests.HTTPError as e:
        messagebox.showerror("Error", f"Failed to fetch weather for {city}: {e}")

# ------------------ UI Elements ------------------
title_label = ctk.CTkLabel(app, text="Weather App", font=("Arial", 24))
title_label.pack(pady=20)

city_frame = ctk.CTkFrame(app, fg_color="#1e1e2f", corner_radius=10)
city_frame.pack(pady=10, padx=20)

def hover_effect(widget, color, original_color):
    def on_enter(e): widget.configure(fg_color=color)
    def on_leave(e): widget.configure(fg_color=original_color)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

for city in cities:
    btn = ctk.CTkButton(city_frame, text=city, width=100, fg_color="#800080", hover_color="#a64ca6",
                        command=lambda c=city: show_weather(c))
    btn.pack(side="left", padx=10, pady=10)
    hover_effect(btn, "#a64ca6", "#800080")

# Weather display
weather_icon = ctk.CTkLabel(app, text="")
weather_icon.pack(pady=10)

city_label = ctk.CTkLabel(app, text="", font=("Arial", 20))
city_label.pack(pady=5)

temp_label = ctk.CTkLabel(app, text="", font=("Arial", 20))
temp_label.pack(pady=5)

desc_label = ctk.CTkLabel(app, text="", font=("Arial", 16))
desc_label.pack(pady=5)

# ------------------ Run App ------------------
app.mainloop()
