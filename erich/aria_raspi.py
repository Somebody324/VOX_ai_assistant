import sys
import random
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk
import csv
import os
import subprocess
import queue
import sounddevice as sd
import json
import threading
import requests
import pyttsx3
from vosk import Model, KaldiRecognizer
import urllib.request
import io
import time

import board
import digitalio
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


WIDTH = 480
HEIGHT = 360

GEMINI_API_KEY = "AIzaSyCwqVfnzllSZQZnPPOoZ3IfrPN0t8h6YNI"  
WEATHER_API_KEY = "9662b07f6e614151874170320252606"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"


def weather_update():
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": "Manila",
        "aqi": "no"
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            weather_data = response.json()

            

            return weather_data
        else:
            return {"error": f"Weather API error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Exception while calling Weather API: {e}"}

def send_to_gemini(user_input):
    headers = {"Content-Type": "application/json"}

    system_message = (
        "You are Aria, a smart, witty, and polite personal assistant AI. "
        "You are helpful, concise, and always respond as if you're speaking to your user personally. "
        "You only answer briefly to all inquiries."
    )

    data = {
        "contents": [
            {
                "parts": [
                    {"text": system_message},
                    {"text": user_input}
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data)
        if response.status_code == 200:
            content = response.json()
            return content['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Exception while calling Gemini: {e}"


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


# class WifiSettingsScreen(tk.Frame):
#     def __init__(self, parent, home_cb, connect_cb, theme):
#         super().__init__(parent, width=480, height=360, bg=theme['bg'])
#         self.theme = theme
#         self.home_cb = home_cb
#         self.connect_cb = connect_cb
#         self.build()

#     def build(self):
#         tk.Label(self, text="Select Wi‑Fi Network", fg=self.theme['fg'], bg=self.theme['bg'], font=("Roboto", 18)).pack(pady=10)
#         self.ssids_frame = tk.Frame(self, bg=self.theme['bg'])
#         self.ssids_frame.pack(fill="both", expand=True)
#         self.scan_ssids()
#         self.create_button("Back", 20, 300, self.home_cb)

#     def create_button(self, text, x, y, cmd):
#         but = tk.Button(self, text=text, command=cmd, width=10)
#         but.place(x=x, y=y)

#     def scan_ssids(self):
#         for widget in self.ssids_frame.winfo_children():
#             widget.destroy()
#         try:
#             output = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,SECURITY', 'device', 'wifi'], text=True)
#             lines = [l for l in output.splitlines() if l and not l.startswith('--')]
#             for idx, line in enumerate(lines):
#                 ssid = line.split(':')[0] or "<Hidden>"
#                 btn = tk.Button(self.ssids_frame, text=ssid, width=40,
#                                 command=lambda s=ssid: self.connect_cb(s))
#                 btn.pack(pady=2)
#         except Exception as e:
#             tk.Label(self.ssids_frame, text="Error scanning Wi‑Fi", fg=self.theme['warn'], bg=self.theme['bg']).pack()

# class WifiConnectScreen(tk.Frame):
#     def __init__(self, parent, ssid, home_cb, theme):
#         super().__init__(parent, width=480, height=360, bg=theme['bg'])
#         self.ssid = ssid
#         self.home_cb = home_cb
#         self.theme = theme
#         self.build()

#     def build(self):
#         tk.Label(self, text=f"Connect to {self.ssid}", fg=self.theme['fg'], bg=self.theme['bg'], font=("Roboto", 18)).pack(pady=10)
#         self.pwd_entry = tk.Entry(self, show="*")
#         self.pwd_entry.pack(pady=5)
#         self.create_button("Connect", 310, 280, self.attempt_connect)
#         self.create_button("Cancel", 20, 280, self.home_cb)

#     def create_button(self, text, x, y, cmd):
#         but = tk.Button(self, text=text, command=cmd, width=10)
#         but.place(x=x, y=y)

#     def attempt_connect(self):
#         pwd = self.pwd_entry.get()
#         subprocess.run(['nmcli', 'device', 'wifi', 'connect', self.ssid, 'password', pwd])
#         self.home_cb()
# erich
class HeartRateReviewScreen(tk.Frame):
    def __init__(self, parent, home_callback, bpm_history, theme):
        super().__init__(parent, width=480, height=360, bg=theme['bg'])
        self.theme = theme
        self.home_callback = home_callback
        self.bpm_history = bpm_history
        self.scroll_start_y = 0
        self.build()

    def build(self):
        t = self.theme

        # Canvas and Scrollable Frame
        self.canvas = tk.Canvas(self, bg=t['bg'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.scrollable = tk.Frame(self.canvas, bg=t['bg'])
        self.scrollable.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.place(x=0, y=30, width=470, height=250)
        self.scrollbar.place(x=470, y=30, height=250)

        # Bind scrolling (mouse + drag)
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.canvas.bind("<ButtonPress-1>", self.start_scroll)
        self.canvas.bind("<B1-Motion>", self.drag_scroll)

        # Add history entries
        for entry in reversed(self.bpm_history):
            self._add_entry(entry)

        # Statistics
        if self.bpm_history:
            vals = [e['bpm'] for e in self.bpm_history]
            avg, mn, mx = sum(vals) // len(vals), min(vals), max(vals)
            avg_color = "#67DE8B" if avg <= 99 else "#E62B2B"
            tk.Label(self, text=f"Avg: {avg}", fg=avg_color, bg=t['bg'], font=("Roboto", 14, "bold")).place(x=20, y=5)
            tk.Label(self, text=f"Min: {mn}", fg=t['fg'], bg=t['bg'], font=("Roboto", 14)).place(x=120, y=5)
            tk.Label(self, text=f"Max: {mx}", fg=t['fg'], bg=t['bg'], font=("Roboto", 14)).place(x=220, y=5)

        # Buttons
        self.create_rounded_button("Export", 25, 300, self.export_bpm_history)
        self.create_rounded_button("Home", 295, 300, self.home_callback)

    def start_scroll(self, event):
        self.scroll_start_y = event.y

    def drag_scroll(self, event):
        delta = self.scroll_start_y - event.y
        self.canvas.yview_scroll(int(delta / 2), "units")
        self.scroll_start_y = event.y

    def create_rounded_button(self, text, x, y, command):
        button_bg = "#2A5062"
        radius = 10
        button = tk.Canvas(self, width=100, height=30, bg=button_bg, highlightthickness=0)
        button.place(x=x, y=y)
        button.create_oval(0, 0, radius * 2, radius * 2, fill=button_bg, outline=button_bg)
        button.create_oval(100 - radius * 2, 0, 100, radius * 2, fill=button_bg, outline=button_bg)
        button.create_rectangle(radius, 0, 100 - radius, 30, fill=button_bg, outline=button_bg)
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
    def __init__(self, parent, heart_callback, mic_callback, theme, toggle_theme):
        super().__init__(parent, width=320, height=240, bg=theme['bg'])
        self.theme = theme
        self.heart_callback = heart_callback
        self.toggle_theme = toggle_theme
        self.mic_callback = mic_callback
        self.icons = {}
        self.spacing = 40
        self.button_width = 140
        self.total_width = 2 * self.button_width + self.spacing
        self.start_x = (480 - self.total_width) // 2
        self.weather_text = "Updating weather ..."
        self.icon_label = tk.Label(self, bg=self.theme['bg'])
        self.icon_label.pack()

        self.build_ui()
        self.update_time()
        self.update_weather()


    def build_ui(self):

        t = self.theme
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))

        def load(name, filename, size):
            try:
                path = os.path.join(base, filename)
                img = Image.open(path).resize(size, Image.Resampling.NEAREST)
                self.icons[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading image {filename}: {e}")
                return False
            return True

        load("wifi", "wifi_white.png" if t['mode'] == 'dark' else "wifi_black.png", (18, 18))
        load("battery", "battery_perma.png", (22, 18))
        load("heart", "heart_icon.png" if t['mode'] == 'dark' else "heart_icon_home_white.png", (140, 140))
        load("mic", "mic_icon.png" if t['mode'] == 'dark' else "mic_icon_home_white.png", (140, 140))
        load("mode", "dark_mode.png" if t['mode'] == 'dark' else "light_mode.png", (18, 18))

        # Top bar icons
        tk.Label(self, image=self.icons["wifi"], bg=t['bg']).place(x=220, y=10)
        tk.Label(self, image=self.icons["battery"], bg=t['bg']).place(x=250, y=10)

        mode_lbl = tk.Label(self, image=self.icons["mode"], bg=t['bg'])
        mode_lbl.place(x=285, y=10)
        mode_lbl.bind("<Button-1>", lambda e: self.toggle_theme())

        # Time and date
        self.time_label = tk.Label(self, text="", fg="#1DCFE3", bg=t['bg'], font=("Roboto", 44, "bold"))
        self.time_label.pack(pady=(10, 0))
        self.date_label = tk.Label(self, text="", fg=t['fg'], bg=t['bg'], font=("Roboto", 14))
        self.date_label.pack(pady=(0, 0))

        # Weather icon and text container
        weather_frame = tk.Frame(self, bg=t['bg'])
        weather_frame.pack(pady=(0, 10))

        self.icon_label = tk.Label(weather_frame, bg=t['bg'])
        self.icon_label.pack(side='left', padx=(0, 10))

        self.weather_label = tk.Label(weather_frame, text=self.weather_text, fg=t['fg'], bg=t['bg'], font=("Roboto", 14, "bold"))
        self.weather_label.pack(side='left')

        # Bottom icons
        heart_btn = tk.Button(self, image=self.icons["heart"], command=self.heart_callback,
                            bg="#0C151C" if t['mode'] == 'dark' else "white",
                            borderwidth=0, activebackground=t['bg'])
        heart_btn.place(x=self.start_x, y=200, width=140, height=140)

        mic_btn = tk.Button(self, image=self.icons["mic"], command=self.mic_callback,
                            bg="#0C151C" if t['mode'] == 'dark' else "white",
                            borderwidth=0, activebackground=t['bg'])
        mic_btn.place(x=self.start_x + self.button_width + self.spacing, y=200, width=140, height=140)

    def update_time(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("%I:%M %p"))
        self.date_label.config(text=now.strftime("%A, %B %d"))
        self.after(1000, self.update_time)

    def update_weather(self):
        try:
            weather_data = weather_update()
            location = weather_data['location']['name']
            temp = weather_data['current']['temp_c']
            feels_like = weather_data['current']['feelslike_c']
            condition = weather_data['current']['condition']['text']
            icon_url = "https:" + weather_data['current']['condition']['icon']

            # Update text
            self.weather_text = f"{round(temp)}°C, Feels like {round(feels_like)}°C\n{condition} | {location}"
            self.weather_label.config(text=self.weather_text)

            # Fetch icon from URL and show
            with urllib.request.urlopen(icon_url) as u:
                raw_data = u.read()
            image = Image.open(io.BytesIO(raw_data)).resize((32, 32), Image.Resampling.NEAREST)
            self.weather_icon = ImageTk.PhotoImage(image)
            self.icon_label.config(image=self.weather_icon)
        except Exception as e:
            print(f"Weather update failed: {e}")
            self.weather_label.config(text="⚠️ Weather unavailable")
            self.icon_label.config(image='')

        self.after(900000, self.update_weather)  # update every 15 minutes
 
            
# erich - done
class HeartRateScreen(tk.Frame):
    def __init__(self, parent, result_cb, theme):
        super().__init__(parent, width=480, height=360, bg=theme['bg'])
        self.theme = theme
        self.result_cb = result_cb
        self.is_animating = False  
        self.animation_id = None   
        self.beat_up = True  # Track beat direction
        self.beat_size = 180  # Initial size
        self.voltage_values = []
        self.build_ui()
    
    def build_ui(self):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
        t = self.theme
        fg_label = "white" if t['mode'] == "dark" else "#0C151C"
        box_bg = "#2A4A62"

        tk.Label(self, text="Heart Rate", fg=fg_label, bg=t['bg'],
                font=("Roboto", 36, "bold")).place(x=(WIDTH - 250) // 2, y=10)

        # Load and store original image for resizing
        self.heart_img_orig = Image.open(os.path.join(base, 'heart_rate_loading.png'))
        self.heart_img_resized = self.heart_img_orig.resize((self.beat_size, self.beat_size), Image.Resampling.NEAREST)
        self.icon = ImageTk.PhotoImage(self.heart_img_resized)
        self.image_label = tk.Label(self, image=self.icon, bg=t['bg'])
        self.image_label.place(x=(WIDTH - self.beat_size) // 2, y=70)

        self.txt = tk.Label(self, text="Measuring...", fg="white", bg=box_bg,
                            font=("Roboto", 20, "bold"), width=20, height=2)
        self.txt.place(x=(WIDTH - 350) // 2, y=280)

    # def start_measurement(self):
    #     if not self.is_animating:  
    #         self.is_animating = True
    #         self.dot = 0
    #         self.animate()
    #         self.beat_heart()  # Start heart animation
    #         self.after(5000, self.complete_measurement)

    def start_measurement(self):
        if not self.is_animating:
            self.is_animating = True
            self.dot = 0
            self.voltage_values = []

            # Setup sensor
            # i2c = busio.I2C(board.SCL, board.SDA)  # Defaults to GPIO3 (SCL) and GPIO2 (SDA)
            # i2c = busio.I2C(scl=digitalio.DigitalInOut(board.D3), sda=digitalio.DigitalInOut(board.D2))
            
            i2c = busio.I2C(board.SCL, board.SDA)
            ads = ADS.ADS1115(i2c)
            chan = AnalogIn(ads, ADS.P0)

            # Start animation and sensor reading
            self.animate()
            self.beat_heart()

            def read_sensor():
                start_time = time.time()
                while time.time() - start_time < 5:
                    voltage = chan.voltage
                    self.voltage_values.append(voltage)
                    time.sleep(0.05)
                self.complete_measurement()

            threading.Thread(target=read_sensor, daemon=True).start()            
            

    def animate(self):
        dots = ["", ".", "..", "..."]
        self.txt.config(text=f"Measuring{dots[self.dot]}")
        self.dot = (self.dot + 1) % 4
        if self.is_animating:
            self.animation_id = self.after(500, self.animate)

    def beat_heart(self):
        if not self.is_animating:
            return

        # Adjust size (scale between 180 and 200 px)
        if self.beat_up:
            self.beat_size += 4
            if self.beat_size >= 200:
                self.beat_up = False
        else:
            self.beat_size -= 4
            if self.beat_size <= 180:
                self.beat_up = True

        # Resize and update image
        resized = self.heart_img_orig.resize((self.beat_size, self.beat_size), Image.Resampling.NEAREST)
        self.icon = ImageTk.PhotoImage(resized)
        self.image_label.config(image=self.icon)
        self.image_label.image = self.icon  # prevent garbage collection

        # Reposition to stay centered
        self.image_label.place(x=(480 - self.beat_size) // 2, y=70)

        # Repeat animation
        self.after(200, self.beat_heart)

    def complete_measurement(self):
        self.stop_animation()
        self.result_cb()

    def stop_animation(self):
        self.is_animating = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
            
            
# erich - done
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
        img = Image.open(img_path).resize((200, 200), Image.Resampling.NEAREST)
        self.icon = ImageTk.PhotoImage(img)
        tk.Label(self, image=self.icon, bg=t['bg']).place(x=30, y=20)

        self.rate = tk.Label(self, text="0", fg=fg_val, bg=t['bg'], font=("Roboto", 60, "bold"))
        self.rate.place(x=240, y=45)
        self.bpm = tk.Label(self, text="BPM", fg=fg_val, bg=t['bg'], font=("Roboto", 22))
        self.bpm.place(x=440, y=80)
        self.status = tk.Label(self, text="Status", fg=fg_val, bg=t['bg'], font=("Roboto", 16))
        self.status.place(x=270, y=135)

        self.create_rounded_button("History", (WIDTH - 220) // 2, 220, self.hist_cb)
        self.create_rounded_button("Home", (WIDTH - 220) // 2, 280, self.home_cb)

    def create_rounded_button(self, text, x, y, command):
        button_bg = "#2A5062"
        radius = 10
        button = tk.Canvas(self, width=220, height=50, bg=button_bg, highlightthickness=0)
        button.place(x=x, y=y)
        button.create_oval(0, 0, radius*2, radius*2, fill=button_bg, outline=button_bg)
        button.create_oval(220-radius*2, 0, 220, radius*2, fill=button_bg, outline=button_bg)
        button.create_rectangle(radius, 0, 220-radius, 50, fill=button_bg, outline=button_bg)
        button.create_text(220 // 2, 25, text=text, fill="white", font=("Roboto", 14, 'bold'))
        button.bind("<Button-1>", lambda e: command())

    def generate_heart_rate(self):
        h = random.randint(60, 140)
        self.rate.config(text=str(h))
        self.bpm_history.insert(0, {'dt': datetime.now(), 'bpm': h})
        status, color, x = ("Normal", "#67DE8B", 334) if h <= 99 else ("Elevated", "#E62B2B", 360)
        self.status.place(x=251, y=155)
        self.bpm.place(x=251, y=125); self.status.config(text=status, fg=color)

# erich - done

class AriaResponseScreen(tk.Frame): 
    def __init__(self, parent, response_text, back_callback, mic_callback, tts_engine, theme):
        super().__init__(parent, width=480, height=360, bg=theme['bg'])
        self.theme = theme
        self.tts_engine = tts_engine
        self.back_callback = back_callback
        self.mic_callback = mic_callback
        self.response_text = response_text
        self.build_ui()

        # Placeholder while waiting for Gemini
        self.text_box.insert("1.0", "Aria is thinking ...")

        # Call Gemini in separate thread
        threading.Thread(target=self.fetch_response_from_gemini, daemon=True).start()

    def fetch_response_from_gemini(self):
        reply = send_to_gemini(self.response_text)
        self.after(0, self.update_text_box, reply)

    def update_text_box(self, new_text):
        self.text_box.config(state="normal")
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", new_text)
        self.text_box.config(state="disabled")
        
        # 🔊 Trigger speech after text is displayed
        threading.Thread(target=self.speak, args=(new_text,), daemon=True).start()


    def build_ui(self):
        t = self.theme
        fg = "white" if t["mode"] == "dark" else "black"

        box_width = 460
        box_height = 220

        # Frame to contain text and scrollbar
        text_frame = tk.Frame(self, bg=t['bg'])
        text_frame.place(x=(480 - box_width) // 2, y=40, width=box_width, height=box_height)

        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        # Text widget
        self.text_box = tk.Text(
            text_frame,
            font=("Roboto", 18, "bold"),
            bg="#2A5062",
            fg="white",
            insertbackground="white",
            borderwidth=0,
            wrap="word",
            padx=10,
            pady=10,
            yscrollcommand=scrollbar.set
        )
        self.text_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.text_box.yview)
        self.text_box.config(state="normal")

        # Bind mouse wheel (Windows, Mac, Linux)
        self.text_box.bind("<Enter>", lambda e: self.text_box.focus_set())
        self.text_box.bind("<MouseWheel>", lambda e: self.text_box.yview_scroll(-1 * (e.delta // 120), "units"))  # Windows/Mac
        self.text_box.bind("<Button-4>", lambda e: self.text_box.yview_scroll(-1, "units"))  # Linux scroll up
        self.text_box.bind("<Button-5>", lambda e: self.text_box.yview_scroll(1, "units"))   # Linux scroll down

        # Enable click-drag scrolling (touchpad/touchscreen style)
        self.text_box.bind("<ButtonPress-1>", self.start_scroll)
        self.text_box.bind("<B1-Motion>", self.scroll_drag)

        self.scroll_start_y = 0  # internal state for drag scroll

        button_width = 220
        spacing = 20
        total_width = button_width * 2 + spacing
        x_start = (480 - total_width) // 2
        y_pos = 290

        self.create_rounded_button("Try Again", x_start, y_pos, self.mic_callback)
        self.create_rounded_button("Home", x_start + button_width + spacing, y_pos, self.back_callback)

    def start_scroll(self, event):
        self.scroll_start_y = event.y

    def scroll_drag(self, event):
        delta = self.scroll_start_y - event.y
        self.text_box.yview_scroll(int(delta / 2), "units")
        self.scroll_start_y = event.y

    def create_rounded_button(self, text, x, y, command):
        button_bg = "#2A5062"
        radius = 10

        button = tk.Canvas(self, width=220, height=50, bg=button_bg, highlightthickness=0, cursor="hand2")
        button.place(x=x, y=y)

        button.create_oval(0, 0, radius * 2, radius * 2, fill=button_bg, outline=button_bg)
        button.create_oval(220 - radius * 2, 0, 220, radius * 2, fill=button_bg, outline=button_bg)
        button.create_rectangle(radius, 0, 220 - radius, 50, fill=button_bg, outline=button_bg)
        button.create_text(110, 25, text=text, fill="white", font=("Roboto", 14, 'bold'))

        button.bind("<Button-1>", lambda e: command())
        return button
    
    def speak(self, response):
        print(f"Starting TTS .....")
        self.master.master.is_speaking = True
        self.tts_engine.say(response)
        self.tts_engine.runAndWait()
        self.tts_engine.stop()
        self.master.master.is_speaking = False
            
        
class MicRecordingScreen(tk.Frame):
    def __init__(self, parent, back_callback, vosk_model, theme):
        super().__init__(parent, width=480, height=360, bg=theme['bg'])
        self.theme = theme
        self.back_callback = back_callback
        self.build_ui()

        # vosk model
        self.model = vosk_model
        self.q = queue.Queue()

        # audio config        
        self.samplerate = 48000
        self.device = 3
        self.device_info = sd.query_devices(kind='input')
        self.input_channels = self.device_info['max_input_channels']
        self.recognizer = KaldiRecognizer(self.model, self.samplerate)

        # state
        self.is_recording = False
        self.recording_thread = None


    def build_ui(self):
        t = self.theme
        fg = "white" if t["mode"] == "dark" else "black"

        box_width = 400
        box_height = 220

        self.text_box = tk.Text(
            self,
            height=10,
            width=50,
            font=("Roboto", 22, "bold"),  # Bold font
            bg="#2A5062",
            fg="white",
            insertbackground="white",
            borderwidth=0,
            wrap="word",
            padx=10,  # Horizontal padding inside the Text widget
            pady=10   # Vertical padding inside the Text widget
        )

        self.text_box.place(x=(480 - box_width)//2, y=70, width=box_width, height=box_height)

        self.placeholder_text = "Speak now..."
        self.text_box.insert("1.0", self.placeholder_text)
        self.text_box.configure(fg="white")

        self.text_box.bind("<FocusIn>", self.clear_placeholder)
        self.text_box.bind("<FocusOut>", self.restore_placeholder)

        self.recording_label = tk.Label(self, text="Recording...", fg=fg, bg=t['bg'], font=("Roboto", 18, "bold"))
        self.recording_label.place(x=(480 - 150)//2, y=310)

        self.create_rounded_button("Back", (480 - 220) // 2, 10, self.back_callback)

        # Store the toggle button for later access
        self.toggle_button = self.create_rounded_button("Start Recording", (480 - 220) // 2, 300, self.toggle_recording)

    def create_rounded_button(self, text, x, y, command):
        button_bg = "#2A5062"
        radius = 10

        button = tk.Canvas(self, width=220, height=50, bg=button_bg, highlightthickness=0, cursor="hand2")
        button.place(x=x, y=y)

        button.create_oval(0, 0, radius * 2, radius * 2, fill=button_bg, outline=button_bg)
        button.create_oval(220 - radius * 2, 0, 220, radius * 2, fill=button_bg, outline=button_bg)
        button.create_rectangle(radius, 0, 220 - radius, 50, fill=button_bg, outline=button_bg)
        text_id = button.create_text(220 // 2, 25, text=text, fill="white", font=("Roboto", 14, 'bold'))

        # Bind click event
        button.bind("<Button-1>", lambda e: command())

        # Store reference to text item for updates
        button.text_id = text_id
        return button

    def update_button_text(self, button, new_text):
        button.itemconfig(button.text_id, text=new_text)

    def clear_placeholder(self, event=None):
        current = self.text_box.get("1.0", "end-1c")
        if current == self.placeholder_text:
            self.text_box.delete("1.0", "end")
            self.text_box.configure(fg="white")

    def restore_placeholder(self, event=None):
        current = self.text_box.get("1.0", "end-1c").strip()
        if not current:
            self.text_box.insert("1.0", self.placeholder_text)
            self.text_box.configure(fg="white")

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio error: {status}")
        self.q.put(bytes(indata))


    def recorder(self):

        try:
            with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype='int16',
                                   channels=1, callback=self.audio_callback, device=self.device):
                while self.is_recording:
                    data = self.q.get()
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        if result.get("text"):
                            print("User:", result["text"])
                            self.clear_placeholder()
                            self.text_box.insert(tk.END, result["text"] + "\n")
                            self.text_box.see(tk.END)
        except Exception as e:
            print(f"Recording error: {e}")

    def toggle_recording(self):
        if not self.is_recording:
            # Start recording
            print('Mic is open, recording ....')
            self.is_recording = True
            self.update_button_text(self.toggle_button, "Stop Recording")
            self.recording_thread = threading.Thread(target=self.recorder, daemon=True)
            self.recording_thread.start()
        else:
            # Stop recording
            print('Mic is closed! recording stopped.')
            self.is_recording = False
            self.update_button_text(self.toggle_button, "Start Recording")
            self.restore_placeholder()
            recorded_text = self.text_box.get("1.0", "end-1c").strip()
            self.master.master.show_aria_response(recorded_text)
            print("\nFull transcription: {recorded_text}")


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Heart Monitor")
        self.geometry("480x360")
        self.attributes("-fullscreen", True)
        self.config(cursor="none")
        self.resizable(False, False)
        self.bpm_history = []
        self.is_dark = True

        # load text to speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 170)
        self.voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', 'english+f3')  # Use
        self.is_speaking = False
        print(sd.query_devices())


        # load model once
        self.LANGUAGE = "english"
        self.MODEL_PATHS = {
            "english": "models/vosk-model-small-en-us-0.15",
        }

        if self.LANGUAGE not in self.MODEL_PATHS:
            raise ValueError("Unsupported language")

        if not os.path.exists(self.MODEL_PATHS[self.LANGUAGE]):
            raise FileNotFoundError(f"Model not found at {self.MODEL_PATHS[self.LANGUAGE]}")


        self.vosk_model = Model(self.MODEL_PATHS[self.LANGUAGE])

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
            ("Home", HomeScreen, (self.container, self.switch_to_heart, self.show_mic, theme, self.toggle_theme)),
            ("Heart",   HeartRateScreen,        (self.container,             self.show_result_screen, theme)),
            ("Result",  HeartRateResultScreen,  (self.container, self.show_home, self.show_review, self.bpm_history, theme)),
            ("Review",  HeartRateReviewScreen,  (self.container, self.show_home, self.bpm_history, theme)),
            # ("WifiList", WifiSettingsScreen,    (self.container, self.show_home, self.goto_connect, theme)),
            # ("WifiConnect", WifiConnectScreen,  (self.container, "", self.show_home, theme)),
            ("Mic", MicRecordingScreen, (self.container, self.show_home, self.vosk_model, theme)),
            ("AriaResponse", AriaResponseScreen, (self.container, "", self.show_home, self.show_mic, self.tts_engine, theme))
        ]:
            frame = cls(*args)
            frame.place(x=0, y=0, width=480, height=360)
            self.frames[name] = frame

        self.show_frame("Home")


    def toggle_theme(self):
        self.is_dark = not self.is_dark
        for f in self.frames.values(): f.destroy()
        self.build_frames(self.current_theme)
    def show_mic(self):

        if self.is_speaking:
            self.tts_engine.stop()
            self.is_speaking = False

        old = self.frames["Mic"]
        old.destroy()

        frame = MicRecordingScreen(self.container, self.show_home, self.vosk_model, self.current_theme)
        frame.place(x=0, y=0, width=480, height=360)
        self.frames["Mic"] = frame
        self.show_frame("Mic") 
        
    def show_aria_response(self, response_text):
        old = self.frames.get("AriaResponse")
        if old:
            old.destroy()

        frame = AriaResponseScreen(self.container, response_text, self.show_home, self.show_mic, self.tts_engine, self.current_theme)
        frame.place(x=0, y=0, width=480, height=360)
        self.frames["AriaResponse"] = frame
        self.show_frame("AriaResponse")


    def show_frame(self, name):
        self.frames[name].tkraise()

    def switch_to_heart(self):
        self.frames["Heart"].start_measurement()
        self.show_frame("Heart")

    def show_result_screen(self):
        self.frames["Result"].generate_heart_rate()
        self.show_frame("Result")

    def show_home(self):
        if self.is_speaking:
            self.tts_engine.stop()
            self.is_speaking

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
