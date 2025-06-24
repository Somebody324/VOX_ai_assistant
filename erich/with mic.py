import sys
import psutil
import random
from PyQt5 import QtSvg

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QVBoxLayout, QStackedWidget, QLabel, QScrollArea, QFrame
)
from PyQt5.QtCore import (Qt, QTimer, QTime, QDate, QDateTime, pyqtSignal)
from PyQt5.QtGui import (QFont, QColor, QPainter, QBrush, QPaintEvent)

# for clickable labels


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()

# ------------------------------
# Home Screen
# ------------------------------

class HomeScreen(QWidget):

    def __init__(self, main_stack, heart_stack, mic_stack):
        super().__init__()
        self.main_stack = main_stack  # Reference to main stack (navigation control, contains other 2 sub stacks)
        self.heart_stack = heart_stack
        self.mic_stack = mic_stack
        self.setFixedSize(320, 240)
        self.setWindowTitle("Home Screen")
        self.initUI()
        self.setupTimer()
        # layout = QVBoxLayout()


    def initUI(self):
        # ----- display contents -----

        
        self.setStyleSheet("background-color: #0C151C;")
        # self.setStyleSheet("background-color: white;")

        self.wifi_icon = QtSvg.QSvgWidget(r"assets\wifi_icon.svg", self)
        self.wifi_icon.setGeometry(110, 19, 16, 16)
        # self.wifi_icon.mousePressEvent = self.wifiClicked

        self.battery_text = QLabel(self)
        self.battery_text.setGeometry(130, 22, 33, 10)
        self.battery_text.setStyleSheet("""
            color: #FFF; font-family: Roboto; font-size: 12px; font-weight: 400; background-color: transparent;
        """)
        self.battery_text.setAlignment(Qt.AlignCenter)
        self.updateBatteryLevel()

        self.battery_icon = QtSvg.QSvgWidget(r"assets\battery_icon.svg", self)
        self.battery_icon.setGeometry(163, 19, 22, 18)
        # self.battery_icon.mousePressEvent = self.batteryClicked/

        self.mode_icon = QtSvg.QSvgWidget(r"assets\dark_light_mode_icon.svg", self)
        self.mode_icon.setGeometry(188, 18, 18, 18)
        # self.mode_icon.mousePressEvent = self.modeClickejkd

        self.time_label = QLabel(self)
        self.time_label.setGeometry(0, 40, 320, 60)
        self.time_label.setStyleSheet("""
            color: #1DCFE3; font-family: Roboto; font-size: 50px; font-weight: 600; letter-spacing: -1px;
        """)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.updateTime()

        self.date_label = QLabel(self)
        self.date_label.setGeometry(0, 95, 320, 20)
        self.date_label.setStyleSheet("""
            color: #FFF; font-family: Roboto; font-size: 16px; font-weight: 400;
        """)
        self.date_label.setAlignment(Qt.AlignCenter)
        self.updateDate()

        self.heart_icon = QtSvg.QSvgWidget(r"assets\heart_icon_hs.svg", self)
        self.heart_icon.setGeometry(62, 129, 95, 100)
 
        self.mic_icon = QtSvg.QSvgWidget(r"assets\mic_icon_hs.svg", self)
        self.mic_icon.setGeometry(169, 129, 95, 100)

        # Button to navigate to heart rate monitor screen & aria mic mode screen

        self.heart_icon.mousePressEvent = self.heartRateModeClicked
        self.mic_icon.mousePressEvent = self.ariaModeClicked
    

    def setupTimer(self):
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.updateTime)
        self.time_timer.start(1000)

        self.battery_timer = QTimer()
        self.battery_timer.timeout.connect(self.updateBatteryLevel)
        self.battery_timer.start(30000)

    def updateTime(self):
        self.time_label.setText(QTime.currentTime().toString("h:mm AP"))

    def updateDate(self):
        self.date_label.setText(QDate.currentDate().toString("dddd, MMMM d"))

    def updateBatteryLevel(self):
        battery = psutil.sensors_battery()
        percent = f"{int(battery.percent)}%" if battery else "56%"
        self.battery_text.setText(percent)

        # click functions

    def heartRateModeClicked(self, event): 
        self.main_stack.setCurrentIndex(1)  # Navigate to heart rate sensing screen

        print("Heart icon clicked")

    def ariaModeClicked(self, event): 
        print("Mic icon clicked")
        self.main_stack.setCurrentIndex(2)  # Navigate to microphone recording screen

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor('#2A4A62')))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(93, 14, 133, 27, 11, 11)
# ------------------------------
# Heart Rate Flow Screens
# ------------------------------

# Screen 1: Heart Rate Sensing
class HeartRateSensing(QWidget):
    def __init__(self, heart_stack):
        super().__init__()
        self.setFixedSize(320, 240)
        self.setStyleSheet("background-color: #0C151C;")
        self.heart_stack = heart_stack
        self.dot_state = 0
        self.initUI()
        self.startAnimation()

    def initUI(self):
        self.title = QLabel("Heart Rate", self)
        self.title.setGeometry(0, 20, 320, 40)
        self.title.setStyleSheet("color: #FFF; font-family: Roboto; font-size: 40px; font-weight: 700;")
        self.title.setAlignment(Qt.AlignCenter)

        self.heart_icon = QtSvg.QSvgWidget(r"assets\heart_rate_ls.svg", self)
        
        self.heart_icon.setGeometry(90, 60, 130, 130)

        self.measure_label = QLabel("Measuring...", self)
        self.measure_label.setGeometry(80, 185, 150, 30)
        self.measure_label.setStyleSheet("""
            color: #FFF; font-family: Roboto; font-size: 18px; font-weight: 500;
            background-color: #2A4A62; border-radius: 11px;
        """)
        self.measure_label.setAlignment(Qt.AlignCenter)

    def startAnimation(self):
        self.dot_state = 0
        self.measure_label.setText("Measuring...")
        # Stop any existing timers before starting new ones
        if hasattr(self, 'dot_timer') and self.dot_timer.isActive():
            self.dot_timer.stop()
        self.dot_timer = QTimer()
        self.dot_timer.timeout.connect(self.animateDots)
        self.dot_timer.start(500)

        if hasattr(self, 'switch_timer') and self.switch_timer.isActive():
            self.switch_timer.stop()
        self.switch_timer = QTimer()
        self.switch_timer.setSingleShot(True)
        self.switch_timer.timeout.connect(self.goToResultScreen)
        self.switch_timer.start(3000)


    def goToResultScreen(self):
        self.heart_stack.setCurrentIndex(1)


    def animateDots(self):
        dots = [".", "..", "..."]
        self.measure_label.setText(f"Measuring{dots[self.dot_state]}")
        self.dot_state = (self.dot_state + 1) % len(dots)
    
    def showEvent(self, event):
        super().showEvent(event)
        self.startAnimation() # ensures startAnimation is called when the screen is shown

    

# Screen 2: Heart Rate Result
class HeartRateResult(QWidget):
    def __init__(self, main_stack, heart_stack, bpm_history):
        super().__init__()
        self.setFixedSize(320, 240)
        self.setStyleSheet("background-color: #0C151C;")
        self.main_stack = main_stack
        self.heart_stack = heart_stack
        self.bpm_history = bpm_history
        self.initUI()

    def initUI(self):
        self.heart_icon = QtSvg.QSvgWidget(r"assets\heart_rate_rs.svg", self)
        self.heart_icon.setGeometry(32, 28, 122, 122)

        self.rate_label = QLabel("0", self)
        self.rate_label.setGeometry(161, 42, 100, 58)
        self.rate_label.setStyleSheet("""
            color: #FFF; font-family: Roboto; font-size: 58px; font-weight: 500;
        """)

        self.bpm_label = QLabel("BPM", self)
        self.bpm_label.setGeometry(234, 80, 60, 20)
        self.bpm_label.setStyleSheet("""
            color: #FFF; font-family: Roboto; font-size: 17px; font-weight: 500;
        """)

        self.status_label = QLabel("Status", self)
        self.status_label.setGeometry(164, 109, 120, 20)
        self.status_label.setAlignment(Qt.AlignLeft)

        # History button
        self.history_label = ClickableLabel("History", self)
        self.history_label.setGeometry(0, 166, 320, 20)
        self.history_label.setStyleSheet("""
            color: #FFF; font-family: Roboto; font-size: 18px; font-weight: 500; background-color: transparent;
        """)
        self.history_label.setAlignment(Qt.AlignCenter)
        # self.history_label.mousePressEvent = self.showHistory

        # Home button
        self.home_label = ClickableLabel("Home", self)
        self.home_label.setGeometry(130, 200, 60, 20)
        self.home_label.setStyleSheet("""
            color: #FFF; font-family: Roboto; font-size: 18px; font-weight: 500; background-color: transparent;
        """)
        self.home_label.setAlignment(Qt.AlignCenter)
        # self.home_label.mousePressEvent = self.backToHome

        self.home_label.clicked.connect(self.returnHome)
        self.history_label.clicked.connect(self.goToHeartRateHistory)

    def returnHome(self):
        print('Home clicked')
        self.main_stack.setCurrentIndex(0)  # Navigate back to home screen
        self.heart_stack.setCurrentIndex(0)  # Reset heart stack to sensing screen

    def goToHeartRateHistory(self):
        print('History Button clicked')
        history_screen = self.heart_stack.widget(2)  # Assuming index 2 is HeartRateHistory
        history_screen.refreshHistory()
        self.heart_stack.setCurrentIndex(2)


    def showEvent(self, event):
        super().showEvent(event)
        self.generateHeartRate()

    def generateHeartRate(self):
        print('generating heart rate')
        self.heart_rate = random.randint(60, 140)
        self.rate_label.setText(str(self.heart_rate))
        print('heart rate: ', self.heart_rate)
        print('bpm history: ', self.bpm_history)



        # Save to history (with timestamp)
        now = QDateTime.currentDateTime()
        self.bpm_history.insert(0, {'dt': now, 'bpm': self.heart_rate})

        if self.heart_rate <= 99:
            status = "Normal"
            color = "#67DE8B"
            bpm_x = 234
        else:
            status = "Elevated"
            color = "#E62B2B"
            bpm_x = 260
        self.bpm_label.move(bpm_x, 80)
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"""
            color: {color}; font-family: Roboto; font-size: 19px; font-weight: 500;
        """)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor('#2A4A62')))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(94, 161, 133, 27, 11, 11)
        painter.drawRoundedRect(94, 195, 133, 27, 11, 11)


# Screen 2: Heart Rate History
class HeartRateHistory(QWidget):
    def __init__(self, main_stack, heart_stack, bpm_history):
        super().__init__()
        self.setFixedSize(320, 240)
        self.setStyleSheet("background-color: #0C151C;")
        self.main_stack = main_stack
        self.heart_stack = heart_stack
        self.bpm_history = bpm_history
        self.initUI()



    def initUI(self):
        # Home button (fixed position at bottom center)
        self.home_label = ClickableLabel("Home", self)
        self.home_label.setGeometry(139, 207, 60, 20)
        self.home_label.setStyleSheet("color: #FFFFFF; font-family: Roboto; font-size: 16px; font-weight: 500;background-color: transparent;")
        self.home_label.setAlignment(Qt.AlignLeft)
        # self.home_label.mousePressEvent = self.goHome

        # Scroll area for BPM entries
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(0, 0, 320, 200)  # Shortened height to avoid covering the Home button
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 4px 2px 4px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #E3F6FA;
                min-height: 36px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
                border: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # Container widget for entries
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.scroll_area.setWidget(self.container)
        self.scroll_area.setWidgetResizable(True)

        # Layout for dynamic content
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(10)

        # Add entries (newest first)
        for entry in reversed(self.bpm_history):
            self.add_entry(entry)

        # Ensure Home label stays clickable
        self.home_label.raise_()
        self.home_label.clicked.connect(self.returnHome)

    def add_entry(self, entry):
        entry_widget = QWidget()
        entry_widget.setFixedSize(290, 50)
        entry_widget.setStyleSheet("background: transparent;")

        # SVG background
        svg_widget = QtSvg.QSvgWidget(r"assets\solid_background.svg", entry_widget)
        svg_widget.setGeometry(0, 0, 284, 50)

        # Date/time
        dt_str = entry['dt'].toString("MM/dd-hh:mm AP")
        dt_label = QLabel(dt_str, entry_widget)
        dt_label.setGeometry(12, 10, 159, 24)
        dt_label.setStyleSheet("color: #FFF; font-family: Roboto; font-size: 20px; font-weight: 500;")

        # BPM
        bpm = entry['bpm']
        bpm_color = "#67DE8B" if bpm < 100 else "#E62B2B"
        bpm_label = QLabel(f"{bpm} BPM", entry_widget)
        bpm_label.setGeometry(190, 10, 85, 24)
        bpm_label.setStyleSheet(f"color: {bpm_color}; font-family: Roboto; font-size: 20px; font-weight: 500;")

        self.layout.addWidget(entry_widget)

    def returnHome(self):

        print('Home clicked')
        self.main_stack.setCurrentIndex(0)  # Navigate back to home screen
        self.heart_stack.setCurrentIndex(0)  # Reset heart stack to sensing screen


    def paintEvent(self, event: QPaintEvent):
        """Draw the rounded rectangle behind the bottom UI area."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect_x = 93
        rect_y = 202
        rect_w = 133
        rect_h = 27

        color = QColor('#2A4A62')
        brush = QBrush(color)

        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect_x, rect_y, rect_w, rect_h, 11, 11)

    def refreshHistory(self):
    # Clear the layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Repopulate with current bpm_history
        for entry in reversed(self.bpm_history):
            self.add_entry(entry)


# ------------------------------

# Microphone Flow Screens
# ------------------------------

# Screen 1: Microphone Recording
class MicrophoneRecording(QWidget):
    def __init__(self, mic_stack):
        super().__init__()
        self.mic_stack = mic_stack  # Controls only microphone screens
        self.setFixedSize(320, 240)
        self.setStyleSheet("background-color: #0C151C;")
        self.initUI()


    
    def initUI(self):
        layout = QVBoxLayout()

        # scroll area for prompt box
        prompt_box = QScrollArea()
        prompt_box.setWidgetResizable(True)


        prompt_box.setFixedSize(300,120)

        prompt_box.setFixedHeight(120)


        prompt_box.setStyleSheet("""
            QScrollArea {
                background: #2A4A62;
                border-radius: 10px;
                
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 4px 2px 4px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #E3F6FA;
                min-height: 36px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
                border: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)


        
        # text container for prompt inside scroll area

        prompt_text_container = QWidget()
        prompt_text_container.setStyleSheet("background-color: transparent; border: 2px solid red")
        prompt_text_container_layout = QVBoxLayout()
    
        # sample prompt inside text container

        prompt_text = QLabel("Who is the fastest man alive?"  )
        prompt_text.setWordWrap(True)
        prompt_text.setStyleSheet("background-color: transparent; padding: 5px; color: white; font-family: Roboto; font-size: 16px; font-weight: 400;")

        
        # add text to container and set layout
        prompt_text_container_layout.addWidget(prompt_text)
        prompt_text_container.setLayout(prompt_text_container_layout)
    
        prompt_box.setWidget(prompt_text_container)

        layout.addWidget(prompt_box)


        recording_icon = QtSvg.QSvgWidget(r"assets\recording_icon.svg", self)
        recording_icon.setFixedSize(66, 66)
        recording_icon.setStyleSheet("border: 2px solid red; background-color: transparent;")

        # Wrap it in a container layout for alignment
        icon_container = QWidget()
        icon_layout = QVBoxLayout()
        icon_layout.addWidget(recording_icon, alignment=Qt.AlignCenter)
        icon_container.setLayout(icon_layout)

        layout.addWidget(icon_container)


        self.title = QLabel("Listening ... ", self)
        self.title.setFixedSize(300, 20)
        self.title.setStyleSheet("color: #FFF; font-family: Roboto; font-size: 16px; font-weight: 700; margin-top: -20px; border: 2px solid red")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        layout.setContentsMargins(10, 10, 10, 10)  # outer padding: left, top, right, bottom
        layout.setSpacing(0)  # no space between widgets

        self.setLayout(layout)


# Screen 2: Microphone Result

class MicrophoneResult(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Microphone Result"))
        self.setLayout(layout)

# ------------------------------
# Main Window
# ------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Flow App")

        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)

        self.setStyleSheet("background-color: #0C151C;")
        # Create bpm_history list to store readings
        self.bpm_history = []

        # --- Heart Rate Screens Stack ---
        self.heart_stack = QStackedWidget()
        heart_sensing = HeartRateSensing(self.heart_stack)
        heart_result = HeartRateResult(self.main_stack, self.heart_stack, self.bpm_history)
        heart_history = HeartRateHistory(self.main_stack, self.heart_stack, self.bpm_history)

        self.heart_stack.addWidget(heart_sensing)  # index 0
        self.heart_stack.addWidget(heart_result)   # index 1
        self.heart_stack.addWidget(heart_history)  # index 2

        # --- Microphone Screens Stack ---
        self.mic_stack = QStackedWidget()
        mic_recording = MicrophoneRecording(self.mic_stack)
        mic_result = MicrophoneResult()
        self.mic_stack.addWidget(mic_recording)  # index 0
        self.mic_stack.addWidget(mic_result)     # index 1

        # --- Home Screen ---
        home = HomeScreen(self.main_stack, self.heart_stack, self.mic_stack)

        # Add all main sections to the main stack
        self.main_stack.addWidget(home)              # index 0
        self.main_stack.addWidget(self.heart_stack)  # index 1
        self.main_stack.addWidget(self.mic_stack)    # index 2

# ------------------------------
# Run the App
# ------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())