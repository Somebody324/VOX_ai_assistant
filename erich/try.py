import sys
import psutil
import random
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk

class HeartRateReviewScreen(tk.Frame):
    def __init__(self, parent, home_callback, bpm_history, theme):
        super().__init__(parent, width=320, height=240, bg=theme['bg'])
        self.theme = theme
        self.home_callback = home_callback
        self.bpm_history = bpm_history
        self.build()

    def build(self):
        t = self.theme
        self.canvas = tk.Canvas(self, bg=t['bg'], highlightthickness=0)
        
        # Create and configure the scrollbar style
        style = ttk.Style()
        if t['mode'] == 'light':
            style.configure('TScrollbar', gripcount=0, background='#2A2A2A', darkcolor='#2A2A2A', lightcolor='#2A2A2A')  # Dark gray color for light mode
        else:
            style.configure('TScrollbar', gripcount=0, background='#333333', darkcolor='#333333', lightcolor='#333333')  # Adjusted for dark mode

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview, style='TScrollbar')
        self.scrollable = tk.Frame(self.canvas, bg=t['bg'])
        self.scrollable.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.place(x=0, y=0, width=310, height=200)
        self.scrollbar.place(x=300, y=0, height=200)
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        for entry in reversed(self.bpm_history):
            self._add_entry(entry)

        if self.bpm_history:
            vals = [e['bpm'] for e in self.bpm_history]
            avg, mn, mx = sum(vals) // len(vals), min(vals), max(vals)
            avg_color = "#67DE8B" if avg <= 99 else "#E62B2B"
            tk.Label(self, text=f"Avg: {avg}", fg=avg_color, bg=t['bg'],
                     font=("Roboto", 12, "bold")).place(x=10, y=205)
            tk.Label(self, text=f"Min: {mn}", fg=t['fg'], bg=t['bg'],
                     font=("Roboto", 12)).place(x=85, y=205)
            tk.Label(self, text=f"Max: {mx}", fg=t['fg'], bg=t['bg'],
                     font=("Roboto", 12)).place(x=150, y=205)

        self.create_rounded_button("Home", 230, 207, self.home_callback)


    def create_rounded_button(self, text, x, y, command):
        button_bg = "#2A5062"
        radius = 10
        button = tk.Canvas(self, width=60, height=20, bg=button_bg, highlightthickness=0)
        button.place(x=x, y=y)
        button.create_oval(0, 0, radius*2, radius*2, fill=button_bg, outline=button_bg)
        button.create_oval(60-radius*2, 0, 60, radius*2, fill=button_bg, outline=button_bg)
        button.create_oval(0, 20-radius*2, radius*2, 20, fill=button_bg, outline=button_bg)
        button.create_oval(60-radius*2, 20-radius*2, 60, 20, fill=button_bg, outline=button_bg)
        button.create_rectangle(radius, 0, 60-radius, 20, fill=button_bg, outline=button_bg)
        button.create_rectangle(0, radius, 60, 20-radius, fill=button_bg, outline=button_bg)
        button.create_text(30, 10, text=text, fill="white", font=("Roboto", 12))
        button.bind("<Button-1>", lambda e: command())

    def _add_entry(self, e):
        t = self.theme
        f = tk.Frame(self.scrollable, bg="#2A5062", width=290, height=50)
        f.pack(pady=5, padx=8)
        dt = e['dt'].strftime("%m/%d-%I:%M %p")
        tk.Label(f, text=dt, fg="white", bg="#2A5062", font=("Roboto", 12)).place(x=12, y=10)
        bpm_color = "#67DE8B" if e['bpm'] < 100 else "#E62B2B"
        tk.Label(f, text=f"{e['bpm']} BPM", fg=bpm_color, bg="#2A5062",
                 font=("Roboto", 12, "bold")).place(x=190, y=10)

class HomeScreen(tk.Frame):
    def __init__(self, parent, heart_callback, theme, toggle_theme):
        super().__init__(parent, width=320, height=240, bg=theme['bg'])
        self.theme = theme
        self.heart_callback = heart_callback
        self.toggle_theme = toggle_theme
        self.icons = {}
        self.build_ui()
        self.update_time()

    def build_ui(self):
        t = self.theme
        base = r"C:\Users\Acer\Desktop\svg"

        def load(name, filename, size):
            try:
                img = Image.open(f"{base}\\{filename}").resize(size, Image.Resampling.LANCZOS)
                self.icons[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading image {filename}: {e}")
                return False
            return True

        if t['mode'] == 'dark':
            load("wifi", "wifi_white.png", (18, 18))
            load("battery", "battery_perma.png", (22, 18))
            load("heart", "heart_icon.png", (100, 100))
            load("mic", "mic_icon.png", (100, 100))
            load("mode", "dark_mode.png", (18, 18))
        else:
            load("wifi", "wifi_black.png", (18, 18))
            load("battery", "battery_perma.png", (22, 18))
            load("heart", "heart_icon_home_white.png", (100, 100))
            load("mic", "mic_icon_home_white.png", (100, 100))
            load("mode", "light_mode.png", (18, 18))

        tk.Label(self, image=self.icons["wifi"], bg=t['bg']).place(x=10, y=10)
        tk.Label(self, image=self.icons["battery"], bg=t['bg']).place(x=260, y=10)
        mode_lbl = tk.Label(self, image=self.icons["mode"], bg=t['bg'])
        mode_lbl.place(x=285, y=10)
        mode_lbl.bind("<Button-1>", lambda e: self.toggle_theme())

        heart_btn = tk.Button(self, image=self.icons["heart"], command=self.heart_callback,
                              bg="#0C151C" if t['mode'] == 'dark' else "white",
                              borderwidth=0, activebackground=t['bg'])
        heart_btn.place(x=50, y=130, width=100, height=100)

        mic_btn = tk.Button(self, image=self.icons["mic"],
                            bg="#0C151C" if t['mode'] == 'dark' else "white",
                            borderwidth=0, activebackground=t['bg'])
        mic_btn.place(x=170, y=130, width=100, height=100)

        self.time_label = tk.Label(self, text="", fg="#1DCFE3", bg=t['bg'], font=("Roboto", 36, "bold"))
        self.time_label.pack(pady=(30, 0))
        self.date_label = tk.Label(self, text="", fg=t['fg'], bg=t['bg'], font=("Roboto", 14))
        self.date_label.pack()

    def update_time(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("%I:%M %p"))
        self.date_label.config(text=now.strftime("%A, %B %d"))
        self.after(1000, self.update_time)

class HeartRateScreen(tk.Frame):
    def __init__(self, parent, result_cb, theme):
        super().__init__(parent, width=320, height=240, bg=theme['bg'])
        self.theme = theme
        self.result_cb = result_cb
        self.build_ui()

    def build_ui(self):
        t = self.theme
        fg_label = "white" if t['mode'] == "dark" else "#0C151C"
        box_bg = "#2A4A62" if t['mode'] == "dark" else "#2A4A62"

        tk.Label(self, text="Heart Rate", fg=fg_label, bg=t['bg'],
                 font=("Roboto", 32, "bold")).pack(pady=10)
        img = Image.open(r"C:\Users\Acer\Desktop\svg\heart rate (loading) png.png")\
                .resize((90, 90), Image.Resampling.LANCZOS)
        self.icon = ImageTk.PhotoImage(img)
        tk.Label(self, image=self.icon, bg=t['bg']).pack()
        self.txt = tk.Label(self, text="Measuring...", fg="white", bg=box_bg,
                            font=("Roboto", 14), width=20)
        self.txt.pack(pady=5)

    def start_measurement(self):
        self.dot = 0
        self.animate()
        self.after(5000, self.result_cb)

    def animate(self):
        dots = ["", ".", "..", "..."]
        self.txt.config(text=f"Measuring{dots[self.dot]}")
        self.dot = (self.dot + 1) % 4
        self.after(500, self.animate)

class HeartRateResultScreen(tk.Frame):
    def __init__(self, parent, home_cb, hist_cb, bpm_history, theme):
        super().__init__(parent, width=320, height=240, bg=theme['bg'])
        self.theme = theme
        self.home_cb = home_cb
        self.hist_cb = hist_cb
        self.bpm_history = bpm_history
        self.build_ui()

    def build_ui(self):
        t = self.theme
        fg_val = t['fg'] if t['mode'] == "dark" else "#0C151C"
        fg_btn = t['fg'] if t['mode'] == "dark" else "black"
        bg_icon = t['bg'] if t['mode'] == "dark" else "white"

        img_path = r"C:\Users\Acer\Desktop\svg\heart_rate_result_white.png" if t['mode'] == 'light' else r"C:\Users\Acer\Desktop\svg\heart rate (results) png.png"
        img = Image.open(img_path).resize((120, 120), Image.Resampling.LANCZOS)
        self.icon = ImageTk.PhotoImage(img)
        tk.Label(self, image=self.icon, bg=bg_icon).place(x=20, y=30)

        self.rate = tk.Label(self, text="0", fg=fg_val, bg=t['bg'], font=("Roboto", 44, "bold"))
        self.rate.place(x=160, y=45)
        self.bpm = tk.Label(self, text="BPM", fg=fg_val, bg=t['bg'], font=("Roboto", 18))
        self.bpm.place(x=234, y=80)
        self.status = tk.Label(self, text="Status", fg=fg_val, bg=t['bg'], font=("Roboto", 16))
        self.status.place(x=170, y=105)

        self.create_rounded_button("History", 110, 155, self.hist_cb)
        self.create_rounded_button("Home", 110, 189, self.home_cb)

    def create_rounded_button(self, text, x, y, command):
        button_bg = "#2A5062"
        radius = 10
        button = tk.Canvas(self, width=100, height=30, bg=button_bg, highlightthickness=0)
        button.place(x=x, y=y)
        button.create_oval(0, 0, radius*2, radius*2, fill=button_bg, outline=button_bg)
        button.create_oval(100-radius*2, 0, 100, radius*2, fill=button_bg, outline=button_bg)
        button.create_oval(0, 30-radius*2, radius*2, 30, fill=button_bg, outline=button_bg)
        button.create_oval(100-radius*2, 30-radius*2, 100, 30, fill=button_bg, outline=button_bg)
        button.create_rectangle(radius, 0, 100-radius, 30, fill=button_bg, outline=button_bg)
        button.create_rectangle(0, radius, 100, 30-radius, fill=button_bg, outline=button_bg)
        button.create_text(50, 15, text=text, fill="white", font=("Roboto", 12))
        button.bind("<Button-1>", lambda e: command())

    def generate_heart_rate(self):
        h = random.randint(60, 140)
        self.rate.config(text=str(h))
        self.bpm_history.insert(0, {'dt': datetime.now(), 'bpm': h})
        status, color, x = ("Normal", "#67DE8B", 234) if h <= 99 else ("Elevated", "#E62B2B", 260)
        self.bpm.place(x=x, y=80); self.status.config(text=status, fg=color)

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Heart Monitor")
        self.geometry("320x240")
        self.resizable(False, False)
        self.bpm_history = []
        self.is_dark = True
        self.themes = {
            'dark': {'mode':'dark','bg':"#0C151C", 'fg':"white", 'accent':"#2A5062", 'ok':"#67DE8B", 'warn':"#E62B2B"},
            'light':{'mode':'light','bg':"white", 'fg':"black", 'accent':"#0C151C", 'ok':"#008000", 'warn':"#FF0000"}
        }
        self.container = tk.Frame(self); self.container.pack(fill="both", expand=True)
        self.frames = {}
        self.build_frames(self.current_theme)

    @property
    def current_theme(self):
        return self.themes['dark'] if self.is_dark else self.themes['light']

    def build_frames(self, theme):
        for name, cls, args in [
            ("Home",    HomeScreen,             (self.container, self.switch_to_heart, theme, self.toggle_theme)),
            ("Heart",   HeartRateScreen,        (self.container, self.show_result_screen, theme)),
            ("Result",  HeartRateResultScreen,  (self.container, self.show_home, self.show_review, self.bpm_history, theme)),
            ("Review",  HeartRateReviewScreen,  (self.container, self.show_home, self.bpm_history, theme)),
        ]:
            frame = cls(*args)
            frame.place(x=0, y=0, width=320, height=240)
            self.frames[name] = frame
        self.show_frame("Home")

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        for f in self.frames.values(): f.destroy()
        self.build_frames(self.current_theme)

    def show_frame(self, name):
        self.frames[name].tkraise()

    def switch_to_heart(self):
        self.frames["Heart"].start_measurement()
        self.show_frame("Heart")

    def show_result_screen(self):
        self.frames["Result"].generate_heart_rate()
        self.show_frame("Result")

    def show_home(self):
        self.show_frame("Home")

    def show_review(self):
        old = self.frames["Review"]
        old.destroy()
        frame = HeartRateReviewScreen(self.container, self.show_home, self.bpm_history, self.current_theme)
        frame.place(x=0, y=0, width=320, height=240)
        self.frames["Review"] = frame
        self.show_frame("Review")


if __name__ == "__main__":
    MainApplication().mainloop()
