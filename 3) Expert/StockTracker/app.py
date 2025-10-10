import yfinance as yf
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
import threading
import time

class StockTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Stock Price Tracker")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1e1e1e")
        
        self.tracked_stocks = {}
        self.price_history = {}
        self.update_interval = 5
        self.running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        control_frame = tk.Frame(main_frame, bg="#2d2d2d", relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(control_frame, text="Stock Symbol:", bg="#2d2d2d", fg="white", font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=10)
        self.symbol_entry = tk.Entry(control_frame, font=("Arial", 11), width=15)
        self.symbol_entry.grid(row=0, column=1, padx=5, pady=10)
        
        add_btn = tk.Button(control_frame, text="Add Stock", command=self.add_stock, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), cursor="hand2")
        add_btn.grid(row=0, column=2, padx=5, pady=10)
        
        remove_btn = tk.Button(control_frame, text="Remove Stock", command=self.remove_stock, bg="#f44336", fg="white", font=("Arial", 10, "bold"), cursor="hand2")
        remove_btn.grid(row=0, column=3, padx=5, pady=10)
        
        self.start_btn = tk.Button(control_frame, text="Start Tracking", command=self.start_tracking, bg="#2196F3", fg="white", font=("Arial", 10, "bold"), cursor="hand2")
        self.start_btn.grid(row=0, column=4, padx=5, pady=10)
        
        self.stop_btn = tk.Button(control_frame, text="Stop Tracking", command=self.stop_tracking, bg="#FF9800", fg="white", font=("Arial", 10, "bold"), cursor="hand2", state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=5, padx=5, pady=10)
        
        tk.Label(control_frame, text="Update Interval (s):", bg="#2d2d2d", fg="white", font=("Arial", 10)).grid(row=0, column=6, padx=10, pady=10)
        self.interval_spinbox = tk.Spinbox(control_frame, from_=1, to=60, width=5, font=("Arial", 10))
        self.interval_spinbox.delete(0, tk.END)
        self.interval_spinbox.insert(0, "5")
        self.interval_spinbox.grid(row=0, column=7, padx=5, pady=10)
        
        content_frame = tk.Frame(main_frame, bg="#1e1e1e")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        list_frame = tk.Frame(content_frame, bg="#2d2d2d", relief=tk.RAISED, bd=2)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(list_frame, text="Tracked Stocks", bg="#2d2d2d", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
        
        tree_frame = tk.Frame(list_frame, bg="#2d2d2d")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Symbol", "Price", "Change", "Change %", "Last Update")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2d2d2d", foreground="white", fieldbackground="#2d2d2d", font=("Arial", 10))
        style.configure("Treeview.Heading", background="#3d3d3d", foreground="white", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", "#4CAF50")])
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        graph_frame = tk.Frame(content_frame, bg="#2d2d2d", relief=tk.RAISED, bd=2)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(graph_frame, text="Price History", bg="#2d2d2d", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.fig = Figure(figsize=(6, 5), facecolor="#2d2d2d")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#1e1e1e")
        self.ax.tick_params(colors="white")
        self.ax.spines["bottom"].set_color("white")
        self.ax.spines["left"].set_color("white")
        self.ax.spines["top"].set_color("white")
        self.ax.spines["right"].set_color("white")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_stock_select)
        
    def add_stock(self):
        symbol = self.symbol_entry.get().strip().upper()
        if not symbol:
            messagebox.showwarning("Input Error", "Please enter a stock symbol")
            return
        
        if symbol in self.tracked_stocks:
            messagebox.showinfo("Info", f"{symbol} is already being tracked")
            return
        
        try:
            stock = yf.Ticker(symbol)
            info = stock.history(period="1d")
            if info.empty:
                messagebox.showerror("Error", f"Could not find stock symbol: {symbol}")
                return
            
            current_price = info["Close"].iloc[-1]
            self.tracked_stocks[symbol] = {
                "price": current_price,
                "prev_price": current_price,
                "change": 0,
                "change_pct": 0,
                "last_update": datetime.now().strftime("%H:%M:%S")
            }
            self.price_history[symbol] = [current_price]
            
            self.tree.insert("", tk.END, iid=symbol, values=(
                symbol,
                f"${current_price:.2f}",
                f"${0:.2f}",
                f"{0:.2f}%",
                self.tracked_stocks[symbol]["last_update"]
            ))
            
            self.symbol_entry.delete(0, tk.END)
            messagebox.showinfo("Success", f"Added {symbol} to tracking")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add stock: {str(e)}")
    
    def remove_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a stock to remove")
            return
        
        symbol = selected[0]
        self.tree.delete(symbol)
        del self.tracked_stocks[symbol]
        del self.price_history[symbol]
        self.update_graph()
        messagebox.showinfo("Success", f"Removed {symbol} from tracking")
    
    def start_tracking(self):
        if not self.tracked_stocks:
            messagebox.showwarning("No Stocks", "Please add at least one stock to track")
            return
        
        self.update_interval = int(self.interval_spinbox.get())
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.tracking_thread = threading.Thread(target=self.update_prices, daemon=True)
        self.tracking_thread.start()
    
    def stop_tracking(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def update_prices(self):
        while self.running:
            for symbol in list(self.tracked_stocks.keys()):
                try:
                    stock = yf.Ticker(symbol)
                    info = stock.history(period="1d")
                    if not info.empty:
                        current_price = info["Close"].iloc[-1]
                        prev_price = self.tracked_stocks[symbol]["price"]
                        change = current_price - prev_price
                        change_pct = (change / prev_price) * 100 if prev_price != 0 else 0
                        
                        self.tracked_stocks[symbol]["prev_price"] = prev_price
                        self.tracked_stocks[symbol]["price"] = current_price
                        self.tracked_stocks[symbol]["change"] = change
                        self.tracked_stocks[symbol]["change_pct"] = change_pct
                        self.tracked_stocks[symbol]["last_update"] = datetime.now().strftime("%H:%M:%S")
                        
                        self.price_history[symbol].append(current_price)
                        if len(self.price_history[symbol]) > 50:
                            self.price_history[symbol].pop(0)
                        
                        self.root.after(0, self.update_tree_item, symbol)
                        
                except Exception as e:
                    print(f"Error updating {symbol}: {str(e)}")
            
            time.sleep(self.update_interval)
    
    def update_tree_item(self, symbol):
        data = self.tracked_stocks[symbol]
        change_color = "green" if data["change"] >= 0 else "red"
        
        self.tree.item(symbol, values=(
            symbol,
            f"${data['price']:.2f}",
            f"${data['change']:.2f}",
            f"{data['change_pct']:.2f}%",
            data["last_update"]
        ))
        
        self.tree.item(symbol, tags=(change_color,))
        self.tree.tag_configure("green", foreground="#4CAF50")
        self.tree.tag_configure("red", foreground="#f44336")
        
        selected = self.tree.selection()
        if selected and selected[0] == symbol:
            self.update_graph()
    
    def on_stock_select(self, event):
        self.update_graph()
    
    def update_graph(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        symbol = selected[0]
        if symbol not in self.price_history:
            return
        
        self.ax.clear()
        prices = self.price_history[symbol]
        
        colors = ["#4CAF50" if i == 0 or prices[i] >= prices[i-1] else "#f44336" for i in range(len(prices))]
        
        self.ax.plot(prices, color="#2196F3", linewidth=2, marker="o", markersize=4)
        self.ax.fill_between(range(len(prices)), prices, alpha=0.3, color="#2196F3")
        
        self.ax.set_title(f"{symbol} Price History", color="white", fontsize=12, fontweight="bold")
        self.ax.set_xlabel("Time Points", color="white")
        self.ax.set_ylabel("Price ($)", color="white")
        self.ax.grid(True, alpha=0.2, color="white")
        
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = StockTrackerApp(root)
    root.mainloop()