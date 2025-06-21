from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QVBoxLayout, QStackedWidget, QLabel
)
import sys

# ------------------------------
# Home Screen
# ------------------------------
class HomeScreen(QWidget):
    def __init__(self, main_stack):
        super().__init__()
        self.main_stack = main_stack  # Reference to main stack (navigation control)

        layout = QVBoxLayout()

        # Button to start Heart Rate flow
        heart_button = QPushButton("Heart Rate Sensing")
        heart_button.clicked.connect(lambda: self.main_stack.setCurrentIndex(1))  # Go to Heart stack

        # Button to start Microphone flow
        mic_button = QPushButton("Microphone Recording")
        mic_button.clicked.connect(lambda: self.main_stack.setCurrentIndex(2))  # Go to Microphone stack

        # Add buttons to layout
        layout.addWidget(heart_button)
        layout.addWidget(mic_button)
        self.setLayout(layout)

# ------------------------------
# Heart Rate Flow Screens
# ------------------------------

# Screen 1: Heart Rate Sensing
class HeartRateSensing(QWidget):
    def __init__(self, heart_stack):
        super().__init__()
        self.heart_stack = heart_stack  # Controls only heart rate screens

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Sensing Heart Rate..."))

        # Simulate ending sensing process
        next_button = QPushButton("Finish Sensing")
        next_button.clicked.connect(lambda: self.heart_stack.setCurrentIndex(1))  # Go to result screen
        layout.addWidget(next_button)

        self.setLayout(layout)

# Screen 2: Heart Rate Result
class HeartRateResult(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Heart Rate Result"))
        self.setLayout(layout)

# ------------------------------
# Microphone Flow Screens
# ------------------------------

# Screen 1: Microphone Recording
class MicrophoneRecording(QWidget):
    def __init__(self, mic_stack):
        super().__init__()
        self.mic_stack = mic_stack  # Controls only microphone screens

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Recording..."))

        # Simulate ending recording
        next_button = QPushButton("Finish Recording")
        next_button.clicked.connect(lambda: self.mic_stack.setCurrentIndex(1))  # Go to result screen
        layout.addWidget(next_button)

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

        # Create the main stack to hold all major screens
        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)

        # Create the Home screen
        home = HomeScreen(self.main_stack)

        # --- Heart Rate Screens Stack ---
        heart_stack = QStackedWidget()
        heart_sensing = HeartRateSensing(heart_stack)
        heart_result = HeartRateResult()
        heart_stack.addWidget(heart_sensing)  # index 0
        heart_stack.addWidget(heart_result)   # index 1

        # --- Microphone Screens Stack ---
        mic_stack = QStackedWidget()
        mic_recording = MicrophoneRecording(mic_stack)
        mic_result = MicrophoneResult()
        mic_stack.addWidget(mic_recording)  # index 0
        mic_stack.addWidget(mic_result)     # index 1

        # Add all main sections to the main stack
        self.main_stack.addWidget(home)        # index 0
        self.main_stack.addWidget(heart_stack) # index 1
        self.main_stack.addWidget(mic_stack)   # index 2

# ------------------------------
# Run the App
# ------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
