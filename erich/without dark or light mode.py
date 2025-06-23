import sys
import psutil
import random
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk

class HeartRateReviewScreen(tk.Frame):
    def __init__(self, parent, home_callback, bpm_history):
        super().__init__(parent, width=320, height=240, bg="#0C151C")
        self.home_callback = home_callback
        self.bpm_history = bpm_history

        # Scrollable area (200px high)
        self.canvas = tk.Canvas(self, width=320, height=200, bg="#0C151C", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#0C151C")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.place(x=0, y=0, width=310, height=200)
        self.scrollbar.place(x=300, y=0, height=200)

        # Add entries
        for entry in reversed(self.bpm_history):
            self.add_entry(entry)

        # Bottom fixed area
        if self.bpm_history:
            values = [entry['bpm'] for entry in self.bpm_history]
            avg = sum(values) // len(values)
            min_bpm = min(values)
            max_bpm = max(values)
            avg_color = "#67DE8B" if avg <= 99 else "#E62B2B"

            tk.Label(self, text=f"Avg: {avg}", fg=avg_color, bg="#0C151C",
                     font=("Roboto", 12, "bold")).place(x=10, y=205)
            tk.Label(self, text=f"Min: {min_bpm}", fg="white", bg="#0C151C",
                     font=("Roboto", 12)).place(x=80, y=205)
            tk.Label(self, text=f"Max: {max_bpm}", fg="white", bg="#0C151C",
                     font=("Roboto", 12)).place(x=150, y=205)

        self.home_button = tk.Label(self, text="Home", fg="white", bg="#2A4A62",
                                    font=("Roboto", 12))
        self.home_button.place(x=230, y=207, width=60, height=20)
        self.home_button.bind("<Button-1>", lambda e: self.home_callback())
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def add_entry(self, entry):
        frame = tk.Frame(self.scrollable_frame, bg="#2A4A62", width=290, height=50)
        frame.pack(pady=5, padx=8)
        dt_str = entry['dt'].strftime("%m/%d-%I:%M %p")
        tk.Label(frame, text=dt_str, fg="white", bg="#2A4A62",
                 font=("Roboto", 12)).place(x=12, y=10)
        bpm = entry['bpm']
        bpm_color = "#67DE8B" if bpm < 100 else "#E62B2B"
        tk.Label(frame, text=f"{bpm} BPM", fg=bpm_color, bg="#2A4A62",
                 font=("Roboto", 12, "bold")).place(x=190, y=10)

class HomeScreen(tk.Frame):
    def __init__(self, parent, heart_callback):
        super().__init__(parent, width=320, height=240, bg="#0C151C")
        self.heart_callback = heart_callback

        self.time_label = tk.Label(self, text="", fg="#1DCFE3", bg="#0C151C",
                                   font=("Roboto", 36, "bold"))
        self.time_label.pack(pady=(30, 0))
        self.date_label = tk.Label(self, text="", fg="white", bg="#0C151C",
                                   font=("Roboto", 14))
        self.date_label.pack()

        # Load icons via PIL once
        self.icons = {}
        def load_icon(key, path, size):
            img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
            self.icons[key] = ImageTk.PhotoImage(img)
            return self.icons[key]

        base = r"C:\Users\Acer\Desktop\svg"
        wifi_img = load_icon("wifi", f"{base}\\wifi icon (home screen) png.png", (18, 18))
        battery_img = load_icon("battery", f"{base}\\battery icon (home) png.png", (22, 18))
        mode_img = load_icon("mode", f"{base}\\dark and light mode icon (home) png.png", (18, 18))
        heart_img = load_icon("heart", f"{base}\\heart icon (home) png.png", (70, 70))
        mic_img = load_icon("mic", f"{base}\\mic icon (home) png.png", (70, 70))

        tk.Label(self, image=wifi_img, bg="#0C151C").place(x=10, y=10)
        tk.Label(self, image=battery_img, bg="#0C151C").place(x=260, y=10)
        tk.Label(self, image=mode_img, bg="#0C151C").place(x=285, y=10)

        self.heart_icon = tk.Button(self, image=heart_img, command=self.heart_callback,
                                    bg="#0C151C", borderwidth=0, activebackground="#0C151C")
        self.heart_icon.place(x=60, y=140, width=70, height=70)
        self.mic_icon = tk.Label(self, image=mic_img, bg="#0C151C")
        self.mic_icon.place(x=170, y=140, width=70, height=70)

        self.update_time()

    def update_time(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("%I:%M %p"))
        self.date_label.config(text=now.strftime("%A, %B %d"))
        self.after(1000, self.update_time)

class HeartRateScreen(tk.Frame):
    def __init__(self, parent, result_callback):
        super().__init__(parent, width=320, height=240, bg="#0C151C")
        self.result_callback = result_callback

        tk.Label(self, text="Heart Rate", fg="white", bg="#0C151C",
                 font=("Roboto", 32, "bold")).pack(pady=10)

        img = Image.open(r"C:\Users\Acer\Desktop\svg\heart rate (loading) png.png") \
                  .resize((90, 90), Image.Resampling.LANCZOS)
        self.load_icon = ImageTk.PhotoImage(img)
        tk.Label(self, image=self.load_icon, bg="#0C151C").pack()

        self.label = tk.Label(self, text="Measuring...", fg="white", bg="#2A4A62",
                              font=("Roboto", 14), width=20)
        self.label.pack(pady=5)

    def start_measurement(self):
        self.dot_state = 0
        self.animate_dots()
        self.after(5000, self.result_callback)

    def animate_dots(self):
        dots = ["", ".", "..", "..."]
        self.label.config(text=f"Measuring{dots[self.dot_state]}")
        self.dot_state = (self.dot_state + 1) % len(dots)
        self.after(500, self.animate_dots)

class HeartRateResultScreen(tk.Frame):
    def __init__(self, parent, home_callback, history_callback, bpm_history):
        super().__init__(parent, width=320, height=240, bg="#0C151C")
        self.home_callback = home_callback
        self.history_callback = history_callback
        self.bpm_history = bpm_history

        img = Image.open(r"C:\Users\Acer\Desktop\svg\heart rate (results) png.png") \
                  .resize((120, 120), Image.Resampling.LANCZOS)
        self.result_icon = ImageTk.PhotoImage(img)
        tk.Label(self, image=self.result_icon, bg="#0C151C").place(x=20, y=30)

        self.rate_label = tk.Label(self, text="0", fg="white", bg="#0C151C",
                                   font=("Roboto", 44, "bold"))
        self.rate_label.place(x=160, y=40)
        self.bpm_label = tk.Label(self, text="BPM", fg="white", bg="#0C151C",
                                  font=("Roboto", 18))
        self.bpm_label.place(x=234, y=80)
        self.status_label = tk.Label(self, text="Status", fg="white", bg="#0C151C",
                                     font=("Roboto", 16))
        self.status_label.place(x=164, y=110)

        self.history_button = tk.Label(self, text="History", fg="white", bg="#0C151C",
                                       font=("Roboto", 14))
        self.history_button.place(x=130, y=166)
        self.history_button.bind("<Button-1>", lambda e: self.history_callback())

        self.home_button = tk.Label(self, text="Home", fg="white", bg="#0C151C",
                                    font=("Roboto", 14))
        self.home_button.place(x=130, y=200)
        self.home_button.bind("<Button-1>", lambda e: self.home_callback())

    def generate_heart_rate(self):
        heart = random.randint(60, 140)
        self.rate_label.config(text=str(heart))
        self.bpm_history.insert(0, {'dt': datetime.now(), 'bpm': heart})
        if heart <= 99:
            status, color, x = "Normal", "#67DE8B", 234
        else:
            status, color, x = "Elevated", "#E62B2B", 260
        self.bpm_label.place(x=x, y=80)
        self.status_label.config(text=status, fg=color)

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Heart Monitor Tkinter")
        self.geometry("320x240")
        self.configure(bg="#0C151C")
        self.resizable(False, False)
        self.bpm_history = []
        self.container = tk.Frame(self, width=320, height=240)
        self.container.pack(fill="both", expand=True)

        self.frames = {
            "HomeScreen": HomeScreen(self.container, self.switch_to_heart),
            "HeartScreen": HeartRateScreen(self.container, self.show_result_screen),
            "ResultScreen": HeartRateResultScreen(self.container,
                                                  self.show_home,
                                                  self.show_review,
                                                  self.bpm_history),
            "ReviewScreen": HeartRateReviewScreen(self.container,
                                                  self.show_home,
                                                  self.bpm_history),
        }
        for f in self.frames.values():
            f.place(x=0, y=0, width=320, height=240)
        self.show_frame("HomeScreen")

    def show_frame(self, name):
        self.frames[name].tkraise()

    def switch_to_heart(self):
        self.frames["HeartScreen"].start_measurement()
        self.show_frame("HeartScreen")

    def show_result_screen(self):
        self.frames["ResultScreen"].generate_heart_rate()
        self.show_frame("ResultScreen")

    def show_home(self):
        self.show_frame("HomeScreen")

    def show_review(self):
        self.frames["ReviewScreen"].destroy()
        self.frames["ReviewScreen"] = HeartRateReviewScreen(self.container,
                                                            self.show_home,
                                                            self.bpm_history)
        self.frames["ReviewScreen"].place(x=0, y=0, width=320, height=240)
        self.show_frame("ReviewScreen")

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
