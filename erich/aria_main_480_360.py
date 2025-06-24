import sys
import random
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk
import csv
import os
import subprocess

def get_battery_voltage():
    try:
        with open('/sys/bus/iio/devices/iio:device0/in_voltage0_raw') as f:
            raw = int(f.read().strip())
        voltage = raw * (1.8 / 4096) * 2
        return voltage
    except Exception:
        return None

def voltage_to_percent(v):
    if v is None: return "--"
    v = max(3.0, min(4.2, v))
    return int((v - 3.0) / (4.2 - 3.0) * 100)

class WifiSettingsScreen(tk.Frame):
    def __init__(self, parent, home_cb, connect_cb, theme):
        super().__init__(parent, width=480, height=360, bg=theme['bg'])
        self.theme = theme
        self.home_cb = home_cb
        self.connect_cb = connect_cb
        self.build()

    def build(self):
        tk.Label(self, text="Select Wi‑Fi Network", fg=self.theme['fg'], bg=self.theme['bg'], font=("Roboto", 18)).pack(pady=10)
        self.ssids_frame = tk.Frame(self, bg=self.theme['bg'])
        self.ssids_frame.pack(fill="both", expand=True)
        self.scan_ssids()
        self.create_button("Back", 20, 300, self.home_cb)

    def create_button(self, text, x, y, cmd):
        but = tk.Button(self, text=text, command=cmd, width=10)
        but.place(x=x, y=y)

    def scan_ssids(self):
        for widget in self.ssids_frame.winfo_children():
            widget.destroy()
        try:
            output = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,SECURITY', 'device', 'wifi'], text=True)
            lines = [l for l in output.splitlines() if l and not l.startswith('--')]
            for idx, line in enumerate(lines):
                ssid = line.split(':')[0] or "<Hidden>"
                btn = tk.Button(self.ssids_frame, text=ssid, width=40,
                                command=lambda s=ssid: self.connect_cb(s))
                btn.pack(pady=2)
        except Exception as e:
            tk.Label(self.ssids_frame, text="Error scanning Wi‑Fi", fg=self.theme['warn'], bg=self.theme['bg']).pack()

class WifiConnectScreen(tk.Frame):
    def __init__(self, parent, ssid, home_cb, theme):
        super().__init__(parent, width=480, height=360, bg=theme['bg'])
        self.ssid = ssid
        self.home_cb = home_cb
        self.theme = theme
        self.build()

    def build(self):
        tk.Label(self, text=f"Connect to {self.ssid}", fg=self.theme['fg'], bg=self.theme['bg'], font=("Roboto", 18)).pack(pady=10)
        self.pwd_entry = tk.Entry(self, show="*")
        self.pwd_entry.pack(pady=5)
        self.create_button("Connect", 310, 280, self.attempt_connect)
        self.create_button("Cancel", 20, 280, self.home_cb)

    def create_button(self, text, x, y, cmd):
        but = tk.Button(self, text=text, command=cmd, width=10)
        but.place(x=x, y=y)

    def attempt_connect(self):
        pwd = self.pwd_entry.get()
        subprocess.run(['nmcli', 'device', 'wifi', 'connect', self.ssid, 'password', pwd])
        self.home_cb()

class HeartRateReviewScreen(tk.Frame):
    def __init__(self, parent, home_callback, bpm_history, theme):
        super().__init__(parent, width=480, height=360, bg=theme['bg'])
        self.theme = theme
        self.home_callback = home_callback
        self.bpm_history = bpm_history
        self.build()

    def build(self):
        t = self.theme
        self.canvas = tk.Canvas(self, bg=t['bg'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg=t['bg'])
        self.scrollable.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.place(x=0, y=30, width=470, height=250)
        self.scrollbar.place(x=470, y=30, height=250)
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        for entry in reversed(self.bpm_history):
            self._add_entry(entry)

        if self.bpm_history:
            vals = [e['bpm'] for e in self.bpm_history]
            avg, mn, mx = sum(vals) // len(vals), min(vals), max(vals)
            avg_color = "#67DE8B" if avg <= 99 else "#E62B2B"
            tk.Label(self, text=f"Avg: {avg}", fg=avg_color, bg=t['bg'], font=("Roboto", 14, "bold")).place(x=20, y=5)
            tk.Label(self, text=f"Min: {mn}", fg=t['fg'], bg=t['bg'], font=("Roboto", 14)).place(x=120, y=5)
            tk.Label(self, text=f"Max: {mx}", fg=t['fg'], bg=t['bg'], font=("Roboto", 14)).place(x=220, y=5)

        self.create_rounded_button("Home", 295, 300, self.home_callback)
        self.create_rounded_button("Export", 25, 300, self.export_bpm_history)

    def create_rounded_button(self, text, x, y, command):
        button_bg = "#2A5062"
        radius = 10
        button = tk.Canvas(self, width=100, height=30, bg=button_bg, highlightthickness=0)
        button.place(x=x, y=y)
        button.create_oval(0, 0, radius*2, radius*2, fill=button_bg, outline=button_bg)
        button.create_oval(100-radius*2, 0, 100, radius*2, fill=button_bg, outline=button_bg)
        button.create_rectangle(radius, 0, 100-radius, 30, fill=button_bg, outline=button_bg)
        button.create_text(50, 15, text=text, fill="white", font=("Roboto", 12))
        button.bind("<Button-1>", lambda e: command())

    def _add_entry(self, e):
        f = tk.Frame(self.scrollable, bg="#2A5062", width=450, height=50)
        f.pack(pady=5, padx=8)
        dt = e['dt'].strftime("%m/%d-%I:%M %p")
        tk.Label(f, text=dt, fg="white", bg="#2A5062", font=("Roboto", 12)).place(x=12, y=10)
        bpm_color = "#67DE8B" if e['bpm'] < 100 else "#E62B2B"
        tk.Label(f, text=f"{e['bpm']} BPM", fg=bpm_color, bg="#2A5062", font=("Roboto", 12, "bold")).place(x=190, y=10)

    def export_bpm_history(self):
        with open('bpm_history.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'BPM'])
            for entry in self.bpm_history:
                writer.writerow([entry['dt'].strftime("%m/%d/%Y %I:%M %p"), entry['bpm']])
        print("BPM history exported to bpm_history.csv")

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
        import os
        from PIL import Image, ImageTk

        t = self.theme
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))


        def load(name, filename, size):
            try:
                path = os.path.join(base, filename)
                img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
                self.icons[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading image {filename}: {e}")
                return False
            return True

        load("wifi", "wifi_white.png" if t['mode'] == 'dark' else "wifi_black.png", (18, 18))
        load("battery", "battery_perma.png", (22, 18))
        load("heart", "heart_icon.png" if t['mode'] == 'dark' else "heart_icon_home_white.png", (180, 180))
        load("mic", "mic_icon.png" if t['mode'] == 'dark' else "mic_icon_home_white.png", (180, 180))
        # load("mode", "dark_mode.png" if t['mode'] == 'dark' else "light_mode.png", (18, 18))


        tk.Label(self, image=self.icons["wifi"], bg=t['bg']).place(x=220, y=10)
        tk.Label(self, image=self.icons["battery"], bg=t['bg']).place(x=250, y=10)
        mode_lbl = tk.Label(self, image=self.icons["mode"], bg=t['bg'])
        mode_lbl.place(x=285, y=10)
        mode_lbl.bind("<Button-1>", lambda e: self.toggle_theme())

        heart_btn = tk.Button(self, image=self.icons["heart"], command=self.heart_callback,
                              bg="#0C151C" if t['mode'] == 'dark' else "white",
                              borderwidth=0, activebackground=t['bg'])
        heart_btn.place(x=50, y=130, width=180, height=180)

        mic_btn = tk.Button(self, image=self.icons["mic"],
                            bg="#0C151C" if t['mode'] == 'dark' else "white",
                            borderwidth=0, activebackground=t['bg'])
        mic_btn.place(x=250, y=130, width=180, height=180)

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
        super().__init__(parent, width=480, height=360, bg=theme['bg'])
        self.theme = theme
        self.result_cb = result_cb
        self.build_ui()
        self.is_animating = False  
        self.animation_id = None   

    def build_ui(self):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
        t = self.theme
        fg_label = "white" if t['mode'] == "dark" else "#0C151C"
        box_bg = "#2A4A62"

        tk.Label(self, text="Heart Rate", fg=fg_label, bg=t['bg'],
                 font=("Roboto", 36, "bold")).pack(pady=10)
        img = Image.open(os.path.join(base,'heart_rate_loading.png'))\
                .resize((90, 90), Image.Resampling.LANCZOS)
        self.icon = ImageTk.PhotoImage(img)
        tk.Label(self, image=self.icon, bg=t['bg']).place(x=190, y=100)
        self.txt = tk.Label(self, text="Measuring...", fg="white", bg=box_bg,
                            font=("Roboto", 14), width=20)
        self.txt.place(x=150, y=280)

    def start_measurement(self):
        if not self.is_animating:  
            self.is_animating = True
            self.dot = 0
            self.animate()
            self.after(5000, self.complete_measurement)  

    def animate(self):
        dots = ["", ".", "..", "..."]
        self.txt.config(text=f"Measuring{dots[self.dot]}")
        self.dot = (self.dot + 1) % 4
        if self.is_animating:  
            self.animation_id = self.after(500, self.animate)

    def complete_measurement(self):
        self.stop_animation()  
        self.result_cb()      

    def stop_animation(self):
        self.is_animating = False   
        if self.animation_id: 
            self.after_cancel(self.animation_id)
            self.animation_id = None

class HeartRateResultScreen(tk.Frame):
    def __init__(self, parent, home_cb, hist_cb, bpm_history, theme):
        super().__init__(parent, width=480, height=360, bg=theme['bg'])
        self.theme = theme
        self.home_cb = home_cb
        self.hist_cb = hist_cb
        self.bpm_history = bpm_history
        self.build_ui()

    def build_ui(self):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
        t = self.theme
        fg_val = t['fg'] if t['mode'] == "dark" else "#0C151C"
        img_path = os.path.join(base,"heart_rate_result_white.png") if t['mode'] == 'light' else os.path.join(base,"heart_rate_result.png")
        img = Image.open(img_path).resize((120, 120), Image.Resampling.LANCZOS)
        self.icon = ImageTk.PhotoImage(img)
        tk.Label(self, image=self.icon, bg=t['bg']).place(x=20, y=30)

        self.rate = tk.Label(self, text="0", fg=fg_val, bg=t['bg'], font=("Roboto", 44, "bold"))
        self.rate.place(x=260, y=45)
        self.bpm = tk.Label(self, text="BPM", fg=fg_val, bg=t['bg'], font=("Roboto", 18))
        self.bpm.place(x=334, y=80)
        self.status = tk.Label(self, text="Status", fg=fg_val, bg=t['bg'], font=("Roboto", 16))
        self.status.place(x=270, y=105)

        self.create_rounded_button("History", 180, 280, self.hist_cb)
        self.create_rounded_button("Home", 180, 320, self.home_cb)

    def create_rounded_button(self, text, x, y, command):
        button_bg = "#2A5062"
        radius = 10
        button = tk.Canvas(self, width=100, height=30, bg=button_bg, highlightthickness=0)
        button.place(x=x, y=y)
        button.create_oval(0, 0, radius*2, radius*2, fill=button_bg, outline=button_bg)
        button.create_oval(100-radius*2, 0, 100, radius*2, fill=button_bg, outline=button_bg)
        button.create_rectangle(radius, 0, 100-radius, 30, fill=button_bg, outline=button_bg)
        button.create_text(50, 15, text=text, fill="white", font=("Roboto", 12))
        button.bind("<Button-1>", lambda e: command())

    def generate_heart_rate(self):
        h = random.randint(60, 140)
        self.rate.config(text=str(h))
        self.bpm_history.insert(0, {'dt': datetime.now(), 'bpm': h})
        status, color, x = ("Normal", "#67DE8B", 334) if h <= 99 else ("Elevated", "#E62B2B", 360)
        self.bpm.place(x=x, y=80); self.status.config(text=status, fg=color)

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Heart Monitor")
        self.geometry("480x360")
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
            ("Heart",   HeartRateScreen,        (self.container,             self.show_result_screen, theme)),
            ("Result",  HeartRateResultScreen,  (self.container, self.show_home, self.show_review, self.bpm_history, theme)),
            ("Review",  HeartRateReviewScreen,  (self.container, self.show_home, self.bpm_history, theme)),
            ("WifiList", WifiSettingsScreen,    (self.container, self.show_home, self.goto_connect, theme)),
            ("WifiConnect", WifiConnectScreen,  (self.container, "", self.show_home, theme)),
        ]:
            frame = cls(*args)
            frame.place(x=0, y=0, width=480, height=360)
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
        frame.place(x=0, y=0, width=480, height=360)
        self.frames["Review"] = frame
        self.show_frame("Review")

    def goto_connect(self, ssid):
        frame = self.frames['WifiConnect']
        frame.ssid = ssid
        frame.destroy()
        frame = WifiConnectScreen(self.container, ssid, self.show_home, self.current_theme)
        frame.place(x=0, y=0, width=480, height=360)
        self.frames['WifiConnect'] = frame
        self.show_frame("WifiConnect")

if __name__ == "__main__":
    MainApplication().mainloop()
