import customtkinter as ctk
from tkinter import Canvas, Frame
from datetime import datetime
import re
import time
from colorsys import rgb_to_hls
import threading

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot Modern GUI")
        self.root.geometry("600x600")
        self.root.minsize(400, 400)  # Make window resizable with minimum size
        self.root.resizable(True, True)

        # Default bubble colors
        self.user_color = "#1a73e8"
        self.bot_color = "#ff00ff"

        self.setup_gui()
        self.bind_events()

    def get_response(self, user_input):
        user_input = user_input.lower().strip()
        if not user_input:
            return "Please enter a message."
        if "hello" in user_input or "hi" in user_input:
            return "Hello How can I help you today"
        elif "your name" in user_input:
            return "I'm PyBot, your friendly assistant"
        elif "how are you" in user_input:
            return "I'm code, but running great 😎"
        elif "bye" in user_input:
            return "Goodbye Have a nice day"
        else:
            return "Sorry, I don't understand that yet."

    def is_valid_hex_color(self, color):
        return bool(re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color))

    def get_contrast_color(self, hex_color):
        try:
            # Remove '#' and convert hex to RGB
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            # Convert to HLS and check lightness
            h, l, s = rgb_to_hls(r/255, g/255, b/255)
            return "#000000" if l > 0.5 else "#FFFFFF"
        except:
            return "#FFFFFF"  # Default to white if color parsing fails

    def setup_gui(self):
        self.chat_canvas = Canvas(self.root, bg="#222222", highlightthickness=0)
        self.chat_frame = Frame(self.chat_canvas, bg="#222222")
        self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.chat_canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)

        self.scrollbar = ctk.CTkScrollbar(self.root, orientation="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y", pady=10)

        self.chat_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))

        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.user_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type a message...")
        self.user_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side="right")

        self.custom_frame = ctk.CTkFrame(self.root)
        self.custom_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(self.custom_frame, text="User Bubble Color").pack(side="left", padx=5)
        self.user_color_entry = ctk.CTkEntry(self.custom_frame, width=100, placeholder_text=self.user_color)
        self.user_color_entry.pack(side="left", padx=5)
        ctk.CTkLabel(self.custom_frame, text="Bot Bubble Color").pack(side="left", padx=5)
        self.bot_color_entry = ctk.CTkEntry(self.custom_frame, width=100, placeholder_text=self.bot_color)
        self.bot_color_entry.pack(side="left", padx=5)
        ctk.CTkButton(self.custom_frame, text="Set Colors", command=self.set_colors).pack(side="left", padx=5)

    def bind_events(self):
        self.user_entry.bind("<Return>", self.send_message)

    def set_colors(self):
        u_color = self.user_color_entry.get().strip()
        b_color = self.bot_color_entry.get().strip()

        if u_color and not self.is_valid_hex_color(u_color):
            self.insert_message("Invalid user color Use a hex code (e.g., #1a73e8).", "bot")
            return
        if b_color and not self.is_valid_hex_color(b_color):
            self.insert_message("Invalid bot color Use a hex code (e.g., #ff00ff).", "bot")
            return

        try:
            if u_color:
                self.user_color = u_color
            if b_color:
                self.bot_color = b_color
            self.insert_message("Colors updated successfully", "bot")
        except Exception as e:
            self.insert_message(f"Error setting colors: {str(e)}", "bot")

    def insert_message(self, msg, sender="user"):
        """Insert a message into the chat frame."""
        timestamp = datetime.now().strftime("%H:%M:%S %p")  # Improved timestamp format
        bubble_color = self.user_color if sender == "user" else self.bot_color
        text_color = self.get_contrast_color(bubble_color)

        bubble_frame = ctk.CTkFrame(self.chat_frame, fg_color=bubble_color, corner_radius=15)
        bubble_label = ctk.CTkLabel(
            bubble_frame,
            text=f"{msg}\n{timestamp}",
            wraplength=400,
            justify="left" if sender == "bot" else "right",
            text_color=text_color
        )
        bubble_label.pack(padx=10, pady=5)

        container = ctk.CTkFrame(self.chat_frame, fg_color="#222222")
        if sender == "user":
            container.pack(anchor="e", pady=5, padx=10, fill="x")
            bubble_frame.pack(side="right", padx=(0, 5))
        else:
            container.pack(anchor="w", pady=5, padx=10, fill="x")
            bubble_frame.pack(side="left", padx=(5, 0))

        self.root.after(50, self.scroll_to_bottom)  # Ensure scrolling after rendering

    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat canvas."""
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def type_bot_message(self, full_msg):
        """Simulate typing animation for bot messages."""
        bubble_frame = ctk.CTkFrame(self.chat_frame, fg_color=self.bot_color, corner_radius=15)
        text_color = self.get_contrast_color(self.bot_color)
        bubble_label = ctk.CTkLabel(
            bubble_frame,
            text="",
            wraplength=400,
            justify="left",
            text_color=text_color
        )
        bubble_label.pack(padx=10, pady=5)
        container = ctk.CTkFrame(self.chat_frame, fg_color="#222222")
        container.pack(anchor="w", pady=5, padx=10, fill="x")
        bubble_frame.pack(side="left", padx=(5, 0))

        displayed = ""
        for char in full_msg:
            displayed += char
            bubble_label.configure(text=displayed)
            self.root.update_idletasks()
            time.sleep(0.02)

        timestamp = datetime.now().strftime("%H:%M:%S %p")
        bubble_label.configure(text=f"{full_msg}\n{timestamp}")
        self.scroll_to_bottom()

    def send_message(self, event=None):
        """Handle sending a message."""
        user_msg = self.user_entry.get().strip()
        if not user_msg:
            self.insert_message("Please type a message before sending.", "bot")
            return

        self.insert_message(user_msg, "user")
        self.user_entry.delete(0, "end")
        bot_msg = self.get_response(user_msg)
        self.root.after(100, lambda: self.type_bot_message(bot_msg))

if __name__ == "__main__":
    app = ctk.CTk()
    chatbot = ChatbotApp(app)
    app.mainloop()