import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon 
from PyQt5.QtGui import QFont
from PyQt5.QtSvg import QSvgWidget
# boilerplate code for the GUI application

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        window_width = 128
        window_height = 160
        
        self.setWindowTitle("Gemini Chatbot GUI")
        self.setGeometry(0, 0, 128, 160) # set window size (128 x 160 TFT Display)
        self.setWindowIcon(QIcon(r"assets\window_icon.png")) # absolute file path
        self.setStyleSheet("background-color: #0c151c;"
                           "padding: 10px;"

                        
                           ) # set background color

        gemini_label = QLabel("Gemini", self)
        gemini_label.setFont(QFont("Roboto", 16))
        gemini_label.setGeometry(0, 0, 128, 50)  
        gemini_label.setAlignment(Qt.AlignCenter)
        gemini_label.setStyleSheet("color: #1dcfe3;"
                            "font-weight: bold;"

                            )
        mic_icon = QSvgWidget(r"assets\mic.svg", parent=self)
        mic_icon.setGeometry((window_width - 50) // 2, 50, 50, 50)

        mic_icon.show()

        # svg_icon.setStyleSheet("color: #FFFFFF;")  # This should make strokes with currentColor white
        listening_label = QLabel("Listening...", self)
        listening_label.setFont(QFont("Roboto", 12))
        listening_label.setGeometry((window_width - 100) // 2, 110, 100, 30)
        listening_label.setAlignment(Qt.AlignCenter)
        listening_label.setStyleSheet("""
            color: white;
            font-weight: semi-bold;
            background-color: #16222e;
            border-radius: 5px;
            padding: 4px;
        """)
        
        
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show() # show window
    sys.exit(app.exec_()) # start the event loop (ensure windows stay)

if __name__ == '__main__':
    main()
        



