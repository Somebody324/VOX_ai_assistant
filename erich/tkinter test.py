import sys
import psutil
import random
import tkinter as tk
from tkinter import ttk
from datetime import datetime

class HeartRateReviewScreen(tk.Frame):
    def __init__(self, parent, home_callback, bpm_history):
        super().__init__(parent, width=320, height=240, bg="#0C151C")
        self.home_callback = home_callback
        self.bpm_history = bpm_history

        self.canvas = tk.Canvas(self, width=320, height=200, bg="#0C151C", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="#0C151C")

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.place(x=0, y=0)
        self.scrollbar.place(x=310, y=0, height=200)

        for entry in reversed(self.bpm_history):
            self.add_entry(entry)

        self.home_button = tk.Label(self, text="Home", fg="white", bg="#2A4A62", font=("Roboto", 12))
        self.home_button.place(x=139, y=207, width=60, height=20)
        self.home_button.bind("<Button-1>", lambda e: self.home_callback())

    def add_entry(self, entry):
        frame = tk.Frame(self.scroll_frame, bg="#2A4A62", width=290, height=50)
        frame.pack(pady=5, padx=8)

        dt_str = entry['dt'].strftime("%m/%d-%I:%M %p")
        dt_label = tk.Label(frame, text=dt_str, fg="white", bg="#2A4A62", font=("Roboto", 12))
        dt_label.place(x=12, y=10)

        bpm = entry['bpm']
        bpm_color = "#67DE8B" if bpm < 100 else "#E62B2B"
        bpm_label = tk.Label(frame, text=f"{bpm} BPM", fg=bpm_color, bg="#2A4A62", font=("Roboto", 12, "bold"))
        bpm_label.place(x=190, y=10)


class HomeScreen(tk.Frame):
    def __init__(self, parent, heart_callback):
        super().__init__(parent, width=320, height=240, bg="#0C151C")
        self.heart_callback = heart_callback

        self.time_label = tk.Label(self, text="", fg="#1DCFE3", bg="#0C151C", font=("Roboto", 36, "bold"))
        self.time_label.pack(pady=(40, 0))

        self.date_label = tk.Label(self, text="", fg="white", bg="#0C151C", font=("Roboto", 14))
        self.date_label.pack()

        self.heart_icon = tk.Button(self, text="❤", command=self.heart_callback)
        self.heart_icon.place(x=90, y=140, width=70, height=70)

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
        self.dot_state = 0
        self.dots = ["", ".", "..", "..."]

        self.title = tk.Label(self, text="Heart Rate", fg="white", bg="#0C151C", font=("Roboto", 32, "bold"))
        self.title.pack(pady=20)

        self.label = tk.Label(self, text="Measuring...", fg="white", bg="#2A4A62", font=("Roboto", 14), width=20)
        self.label.pack(pady=50)

    def start_measurement(self):
        self.dot_state = 0
        self.animate_dots()
        self.after(5000, self.result_callback)

    def animate_dots(self):
        self.label.config(text=f"Measuring{self.dots[self.dot_state]}")
        self.dot_state = (self.dot_state + 1) % len(self.dots)
        self.after(500, self.animate_dots)


class HeartRateResultScreen(tk.Frame):
    def __init__(self, parent, home_callback, history_callback, bpm_history):
        super().__init__(parent, width=320, height=240, bg="#0C151C")
        self.home_callback = home_callback
        self.history_callback = history_callback
        self.bpm_history = bpm_history

        self.rate_label = tk.Label(self, text="0", fg="white", bg="#0C151C", font=("Roboto", 44, "bold"))
        self.rate_label.place(x=160, y=40)

        self.bpm_label = tk.Label(self, text="BPM", fg="white", bg="#0C151C", font=("Roboto", 18))
        self.bpm_label.place(x=234, y=80)

        self.status_label = tk.Label(self, text="Status", fg="white", bg="#0C151C", font=("Roboto", 16))
        self.status_label.place(x=164, y=110)

        self.history_button = tk.Label(self, text="History", fg="white", bg="#0C151C", font=("Roboto", 14))
        self.history_button.place(x=130, y=166)
        self.history_button.bind("<Button-1>", lambda e: self.history_callback())

        self.home_button = tk.Label(self, text="Home", fg="white", bg="#0C151C", font=("Roboto", 14))
        self.home_button.place(x=130, y=200)
        self.home_button.bind("<Button-1>", lambda e: self.home_callback())

    def generate_heart_rate(self):
        heart_rate = random.randint(60, 140)
        self.rate_label.config(text=str(heart_rate))
        self.bpm_history.insert(0, {'dt': datetime.now(), 'bpm': heart_rate})

        if heart_rate <= 99:
            status = "Normal"
            color = "#67DE8B"
            self.bpm_label.place(x=234, y=80)
        else:
            status = "Elevated"
            color = "#E62B2B"
            self.bpm_label.place(x=260, y=80)

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

        self.frames = {}
        self.create_frames()

        self.show_frame("HomeScreen")

    def create_frames(self):
        self.frames["HomeScreen"] = HomeScreen(self.container, self.switch_to_heart)
        self.frames["HeartScreen"] = HeartRateScreen(self.container, self.show_result_screen)
        self.frames["ResultScreen"] = HeartRateResultScreen(self.container, self.show_home, self.show_review, self.bpm_history)
        self.frames["ReviewScreen"] = HeartRateReviewScreen(self.container, self.show_home, self.bpm_history)

        for frame in self.frames.values():
            frame.place(x=0, y=0, width=320, height=240)

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

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
        self.frames["ReviewScreen"] = HeartRateReviewScreen(self.container, self.show_home, self.bpm_history)
        self.frames["ReviewScreen"].place(x=0, y=0, width=320, height=240)
        self.show_frame("ReviewScreen")


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
