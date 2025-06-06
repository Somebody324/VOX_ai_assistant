import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QDialog, QListWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QTime, QDate, QSize, QPointF
from PyQt5.QtGui import QFont, QIcon, QPainter, QPixmap, QColor, QPainterPath, QPen


class PulseWaveform(QWidget):
    def __init__(self, color=QColor("#1dcfe3"), parent=None):
        super().__init__(parent)
        self.phase = 0
        self.color = color
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(40)

    def animate(self):
        self.phase = (self.phase + 0.15) % (2 * math.pi)
        self.update()

    def paintEvent(self, event):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.color, max(2, h // 10))
        painter.setPen(pen)
        mid = h // 2
        points = []
        for x in range(w):
            t = (x / w) * 2 * math.pi + self.phase
            y = mid + math.sin(t) * (h * 0.25) + math.sin(t * 4) * (h * 0.08)
            points.append((x, int(y)))
        for i in range(1, len(points)):
            painter.drawLine(points[i - 1][0], points[i - 1][1], points[i][0], points[i][1])


class HistoryScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BP Readings")
        self.setStyleSheet("background-color: #000; color: white;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        title_label = QLabel("BP Readings")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        self.readings_list = QListWidget()
        readings = [
            "120/80 mmHg",
            "115/75 mmHg",
            "130/85 mmHg",
            "110/70 mmHg",
            "125/78 mmHg"
        ]
        self.readings_list.addItems(readings)
        main_layout.addWidget(self.readings_list)

        self.setLayout(main_layout)


class BPStatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(0)

        # Theme toggle (left)
        self.theme_toggle = QPushButton()
        self.theme_toggle.setFixedSize(24, 24)
        self.theme_toggle.setStyleSheet("background: transparent; border: none;")
        self.theme_toggle.setIcon(QIcon(self.draw_theme_icon(24, 24, QColor("#1dcfe3"), QColor("#0c151c"))))
        layout.addWidget(self.theme_toggle, alignment=Qt.AlignLeft)

        layout.addStretch()

        # Battery icon (right)
        self.battery = QLabel()
        self.battery.setFixedSize(28, 18)
        self.battery.setPixmap(self.draw_battery_icon(28, 18, QColor("#1dcfe3")))
        layout.addWidget(self.battery, alignment=Qt.AlignRight)

        self.setLayout(layout)
        self.is_dark_mode = True
        self.parent = parent

        self.theme_toggle.clicked.connect(self.toggle_theme)

    def draw_battery_icon(self, width, height, color):
        pix = QPixmap(width, height)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setPen(color)
        body_w = int(width * 0.7)
        body_h = int(height * 0.6)
        p.drawRect(1, (height - body_h) // 2, body_w, body_h)
        p.fillRect(2, (height - body_h) // 2 + 1, body_w - 3, body_h - 2, QColor("#2ECC40"))
        tip_w = max(1, int(width * 0.15))
        tip_h = max(1, int(height * 0.2))
        p.drawRect(body_w + 1, (height - tip_h) // 2, tip_w, tip_h)
        p.end()
        return pix

    def draw_theme_icon(self, width, height, color, fill):
        pix = QPixmap(width, height)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(color)
        p.setPen(Qt.NoPen)
        p.drawEllipse(int(width * 0.15), int(height * 0.15), int(width * 0.7), int(height * 0.7))
        p.setBrush(fill)
        p.drawEllipse(int(width * 0.33), int(height * 0.15), int(width * 0.5), int(height * 0.7))
        p.end()
        return pix

    def toggle_theme(self):
        # Toggle between dark and light mode for the parent dialog
        if self.parent:
            if self.is_dark_mode:
                self.parent.setStyleSheet("background-color: #fff; color: #0c151c;")
                self.parent.heart_widget.set_ray_color(QColor("black"))  # Change heart ray color to black
            else:
                self.parent.setStyleSheet("background-color: #0c151c; color: #1dcfe3;")
                self.parent.heart_widget.set_ray_color(QColor("white"))  # Change heart ray color to white
            self.is_dark_mode = not self.is_dark_mode


class PulseScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pulse Monitor")
        self.setMinimumSize(160, 160)
        self.resize(300, 300)  # initial size, window is resizable now

        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add the custom status bar at the top
        self.status_bar = BPStatusBar(parent=self)
        main_layout.addWidget(self.status_bar)

        # Content layout (everything else goes here)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(5)

        # Title
        self.title_label = QLabel("PULSE")
        self.title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.title_label)

        # Custom heart widget with rays
        self.heart_widget = HeartWidget()
        self.heart_widget.setMinimumHeight(80)
        content_layout.addWidget(self.heart_widget, alignment=Qt.AlignCenter)

        # Measuring text
        self.measuring_label = QLabel("Measuring...")
        self.measuring_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.measuring_label)

        # BPM value
        self.bpm_label = QLabel("78 bpm")
        self.bpm_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.bpm_label)

        # Bottom buttons
        self.button_layout = QHBoxLayout()
        self.history_button = QPushButton("History")
        self.back_button = QPushButton("Back")

        self.history_button.setStyleSheet("background-color: #003f5c; color: cyan;")
        self.back_button.setStyleSheet("background-color: #003f5c; color: white;")

        self.button_layout.addWidget(self.history_button)
        self.button_layout.addWidget(self.back_button)
        content_layout.addLayout(self.button_layout)

        # Add content layout to main layout
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        # Timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_heart)
        self.timer.start(100)

        # History storage
        self.history = []
        self.history_button.clicked.connect(self.show_history)
        self.back_button.clicked.connect(self.close)

        # Simulated BPM update for demonstration (optional)
        self.bpm_timer = QTimer()
        self.bpm_timer.timeout.connect(self.update_bpm)
        self.bpm_timer.start(3000)

        self.update_fonts()

    def update_fonts(self):
        w = self.width()
        h = self.height()
        scale_factor = min(w / 160, h / 128)
        self.title_label.setFont(QFont("Arial", max(int(10 * scale_factor), 1), QFont.Bold))
        self.measuring_label.setFont(QFont("Arial", max(int(9 * scale_factor), 1)))
        self.bpm_label.setFont(QFont("Arial", max(int(15 * scale_factor), 1), QFont.Bold))
        self.history_button.setFont(QFont("Arial", max(int(8 * scale_factor), 1)))
        self.back_button.setFont(QFont("Arial", max(int(8 * scale_factor), 1)))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_fonts()
        self.heart_widget.setFixedHeight(int(self.height() * 0.35))  # Keep heart compact on resize

    def animate_heart(self):
        self.heart_widget.animate()

    def update_bpm(self):
        import random, datetime
        new_bpm = random.randint(60, 100)
        self.bpm_label.setText(f"{new_bpm} bpm")
        self.measuring_label.setText("Measuring...")
        self.history.append((datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), new_bpm))

    def show_history(self):
        if self.history:
            history_text = "\n".join([f"{t}: {bpm} bpm" for t, bpm in self.history[-10:]])
        else:
            history_text = "No History Available"
        QMessageBox.information(self, "Pulse History (last 10)", history_text)


class HeartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.heart_scale = 1.0
        self.rays_scale = 1.0
        self.scale_direction = 1
        self.setMinimumSize(80, 80)
        self.ray_color = QColor("white")  # Default to white for dark mode

    def set_ray_color(self, color: QColor):
        self.ray_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        center = QPointF(w / 2, h / 2)

        # Clear background
        painter.setBackgroundMode(Qt.TransparentMode)

        # Define the max size for heart + rays, with padding
        max_diameter = min(w, h) * 0.75  # 75% of smaller dimension for combined heart + rays

        # Separate heart and rays diameters with scale applied
        rays_diameter = max_diameter * self.rays_scale
        heart_diameter = max_diameter * 0.7 * self.heart_scale  # Heart slightly smaller than rays

        # Draw rays - 12 rays evenly spaced around center
        rays_radius_inner = rays_diameter / 2 * 0.65
        rays_length = rays_diameter / 2 * 0.3
        ray_color = QColor(self.ray_color)
        ray_color.setAlpha(130)
        pen = QPen(ray_color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        ray_count = 12
        for i in range(ray_count):
            angle_deg = (360 / ray_count) * i
            angle_rad = math.radians(angle_deg)
            x1 = center.x() + rays_radius_inner * math.cos(angle_rad)
            y1 = center.y() + rays_radius_inner * math.sin(angle_rad)
            x2 = center.x() + (rays_radius_inner + rays_length) * math.cos(angle_rad)
            y2 = center.y() + (rays_radius_inner + rays_length) * math.sin(angle_rad)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Draw heart as a fuller shape closer to ❤️ emoji:
        path = QPainterPath()

        size = heart_diameter
        # Invert the y coordinates to flip heart upright
        path.moveTo(0, -size * 0.25)

        # Left side (fuller and rounded)
        path.cubicTo(
            QPointF(-size * 0.5, -size * 0.85),
            QPointF(-size * 0.9, -size * 0.15),
            QPointF(0, size * 0.4)
        )

        # Right side (mirror)
        path.cubicTo(
            QPointF(size * 0.9, -size * 0.15),
            QPointF(size * 0.5, -size * 0.85),
            QPointF(0, -size * 0.25)
        )
        path.closeSubpath()

        painter.save()
        painter.translate(center)
        painter.setPen(QPen(QColor("red"), 2))
        painter.setBrush(QColor("red"))
        painter.drawPath(path)
        painter.restore()

    def animate(self):
        if self.scale_direction == 1:
            self.heart_scale += 0.02
            self.rays_scale += 0.01
            if self.heart_scale >= 1.1:
                self.scale_direction = -1
        else:
            self.heart_scale -= 0.02
            self.rays_scale -= 0.01
            if self.heart_scale <= 1.0:
                self.scale_direction = 1
        self.update()


class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        self.battery = QLabel()
        layout.addWidget(self.battery)

        self.wifi = QLabel()
        layout.addWidget(self.wifi)

        self.settings = QPushButton()
        self.settings.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.settings)

        self.theme_toggle = QPushButton()
        self.theme_toggle.setStyleSheet("background: transparent; border: none;")
        self.theme_toggle.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_toggle)

        self.setLayout(layout)
        self.is_dark_mode = True
        self.icon_color = QColor("1dcfe3")
        self.icon_fill = QColor("#0c151c")
        self.parent = parent

        self.resize_icons()

    def toggle_theme(self):
        if self.is_dark_mode:
            self.parent.setStyleSheet(
                "background-color: #ffffff; color: #0c151c; font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;"
            )  # Light blue background, white text
            self.icon_color = QColor("0c151c")
            self.icon_fill = QColor("#ffffff")
        else:
            self.parent.setStyleSheet(
                "background-color: #0c151c; color: #0c151c; font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;"
            )  # Dark blue background, light blue text
            self.icon_color = QColor("#1dcfe3")
            self.icon_fill = QColor("#0c151c")

        self.is_dark_mode = not self.is_dark_mode
        self.resize_icons()

    def draw_battery_icon(self, width, height, color):
        pix = QPixmap(width, height)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setPen(color)
        body_w = int(width * 0.7)
        body_h = int(height * 0.6)
        p.drawRect(1, (height - body_h) // 2, body_w, body_h)
        p.fillRect(2, (height - body_h) // 2 + 1, body_w - 3, body_h - 2, QColor("#2ECC40"))
        tip_w = max(1, int(width * 0.15))
        tip_h = max(1, int(height * 0.2))
        p.drawRect(body_w + 1, (height - tip_h) // 2, tip_w, tip_h)
        p.end()
        return pix

    def draw_wifi_icon(self, width, height, color):
        pix = QPixmap(width, height)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        pen = p.pen()
        pen.setColor(color)
        pen.setWidth(max(1, width // 12))
        p.setPen(pen)
        p.drawArc(int(width * 0.1), int(height * 0.4), int(width * 0.8), int(height * 0.6), 0 * 16, 180 * 16)
        p.drawArc(int(width * 0.25), int(height * 0.6), int(width * 0.5), int(height * 0.4), 0 * 16, 180 * 16)
        p.drawArc(int(width * 0.45), int(height * 0.8), int(width * 0.1), int(height * 0.2), 0 * 16, 180 * 16)
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        dot_size = max(2, width // 8)
        p.drawEllipse(int(width * 0.6), int(height * 0.9), dot_size, dot_size)
        p.end()
        return pix

    def draw_settings_icon(self, width, height, color, fill):
        pix = QPixmap(width, height)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(color)
        p.setPen(Qt.NoPen)
        center = pix.rect().center()
        radius = min(width, height) * 0.3
        teeth = 8
        tooth_width = max(1, int(min(width, height) * 0.08))
        tooth_height = max(2, int(min(width, height) * 0.15))
        for i in range(teeth):
            angle = (360 / teeth) * i
            p.save()
            p.translate(center)
            p.rotate(angle)
            p.drawRect(-tooth_width // 2, -int(radius) - tooth_height, tooth_width, tooth_height)
            p.restore()
        p.drawEllipse(center, int(radius), int(radius))
        p.setBrush(fill)
        p.drawEllipse(center, int(radius * 0.4), int(radius * 0.4))
        p.end()
        return pix

    def draw_theme_icon(self, width, height, color, fill):
        pix = QPixmap(width, height)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(color)
        p.setPen(Qt.NoPen)
        p.drawEllipse(int(width * 0.15), int(height * 0.15), int(width * 0.7), int(height * 0.7))
        p.setBrush(fill)
        p.drawEllipse(int(width * 0.33), int(height * 0.15), int(width * 0.5), int(height * 0.7))
        p.end()
        return pix

    def resize_icons(self):
        h = self.height()
        battery_w = max(20, int(h * 20 / 24))
        battery_h = max(14, int(h * 14 / 24))
        wifi_w = max(24, int(h * 24 / 24))
        wifi_h = max(20, int(h * 20 / 24))
        icon_size = max(24, h)

        self.battery.setFixedSize(battery_w, battery_h)
        self.battery.setPixmap(self.draw_battery_icon(battery_w, battery_h, self.icon_color))

        self.wifi.setFixedSize(wifi_w, wifi_h)
        self.wifi.setPixmap(self.draw_wifi_icon(wifi_w, wifi_h, self.icon_color))

        self.settings.setFixedSize(icon_size, icon_size)
        self.settings.setIcon(QIcon(self.draw_settings_icon(icon_size, icon_size, self.icon_color, self.icon_fill)))
        self.settings.setIconSize(QSize(icon_size, icon_size))

        self.theme_toggle.setFixedSize(icon_size, icon_size)
        self.theme_toggle.setIcon(QIcon(self.draw_theme_icon(icon_size, icon_size, self.icon_color, self.icon_fill)))
        self.theme_toggle.setIconSize(QSize(icon_size, icon_size))


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smartwatch Dashboard - Resizable")
        self.resize(160, 128)
        self.setMinimumSize(160, 128)
        self.setStyleSheet(
            "background-color: #0c151c; color: #1dcfe3; font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; border-radius: 8px;"
        )

        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setStyleSheet("color: #1dcfe3; font-weight: 700; letter-spacing: 0.8px; font-family: 'Roboto';")

        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("color: #1dcfe3; font-weight: 500; letter-spacing: 0.5px; font-family: 'Roboto';")

        self.update_clock()
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)

        self.pulse_btn = QPushButton()
        self.pulse_btn.setStyleSheet(
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1dcfe3, stop:1 #285D9B); border-radius: 10px; color: white; font-weight: 600; font-family: 'Roboto';"
        )
        self.pulse_btn.clicked.connect(self.open_pulse_screen)

        self.ai_btn = QPushButton()
        self.ai_btn.setStyleSheet(
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1dcfe3, stop:1 #285D9B); border-radius: 10px; color: white; font-weight: 600; font-family: 'Roboto';"
        )

        top_layout = QVBoxLayout()
        top_layout.setContentsMargins(4, 4, 4, 0)
        top_layout.setSpacing(0)
        top_layout.addWidget(self.clock_label)
        top_layout.addWidget(self.date_label)

        center_icon_layout = QHBoxLayout()
        center_icon_layout.setSpacing(20)
        center_icon_layout.setContentsMargins(4, 4, 4, 4)
        center_icon_layout.setAlignment(Qt.AlignCenter)
        center_icon_layout.addWidget(self.pulse_btn)
        center_icon_layout.addWidget(self.ai_btn)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(6)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(center_icon_layout)
        main_layout.addStretch()

        self.status_bar = StatusBar(self)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)

        self._min_width = 160
        self._min_height = 128
        self._min_font_size_clock = 14
        self._min_font_size_date = 8
        self._min_btn_size = 48

        self.resizeEvent(None)

    def open_pulse_screen(self):
        self.pulse_screen = PulseScreen()
        # Removed fixed size to make window freely resizable
        # self.pulse_screen.setFixedSize(300, 300)
        self.pulse_screen.show()

    def update_clock(self):
        current_time = QTime.currentTime()
        self.clock_label.setText(current_time.toString("hh:mm AP"))
        self.date_label.setText(QDate.currentDate().toString("ddd, MMM d"))

    def resizeEvent(self, event):
        w = max(self.width(), self._min_width)
        h = max(self.height(), self._min_height)

        clock_font_size = max(self._min_font_size_clock, int(h * 14 / self._min_height))
        date_font_size = max(self._min_font_size_date, int(h * 8 / self._min_height))

        self.clock_label.setFont(QFont("Roboto", clock_font_size, QFont.Bold))
        self.date_label.setFont(QFont("Roboto", date_font_size))

        btn_size = max(self._min_btn_size, int(h * 48 / self._min_height))
        self.pulse_btn.setFixedSize(btn_size, btn_size)
        self.ai_btn.setFixedSize(btn_size, btn_size)

        self.pulse_btn.setIcon(QIcon(self.draw_heart_icon(btn_size)))
        self.pulse_btn.setIconSize(QSize(btn_size, btn_size))

        self.ai_btn.setIcon(QIcon(self.draw_mic_icon(btn_size)))
        self.ai_btn.setIconSize(QSize(btn_size, btn_size))

        self.status_bar.resize_icons()
        super().resizeEvent(event)

    def draw_heart_icon(self, size):
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor("white"))
        p.setPen(Qt.NoPen)
        path = QPainterPath()
        path.moveTo(size / 2, size * 0.79)
        path.cubicTo(size * 0.125, size * 0.42, size * 0.29, size * 0.08, size / 2, size * 0.29)
        path.cubicTo(size * 0.71, size * 0.08, size * 0.875, size * 0.42, size / 2, size * 0.79)
        p.drawPath(path)
        p.end()
        return pix

    def draw_mic_icon(self, size):
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setBrush(QColor("white"))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(int(size * 0.375), int(size * 0.208), int(size * 0.25), int(size * 0.375), int(size * 0.125), int(size * 0.125))
        p.drawRect(int(size * 0.458), int(size * 0.583), int(size * 0.083), int(size * 0.25))
        p.drawEllipse(int(size * 0.375), int(size * 0.833), int(size * 0.25), int(size * 0.083))
        p.end()
        return pix


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())