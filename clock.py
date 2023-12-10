import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt, QPoint, QTimer, QTime, QEvent
from PyQt5.QtGui import QCursor, QIcon  # Add QCursor from QtGui module
import json
import ctypes
import sys
import os

class EzClock(QMainWindow):
    CONFIG_FILE = '.clock_config.json'

    def __init__(self):
        super().__init__()

        # Set application identifier for Windows taskbar
        myappid = 'com.ezClock.clock.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Set window properties
        self.setWindowTitle("Your Window Title")
        self.setGeometry(100, 100, 700, 700)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create central widget and layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)

        # Color options for the clock text
        self.color_list = ["white", 'black', '#FF0000']
        self.color_index = 0
        
        # Set window icon
        icon_path = EzClock.resource_path("res/icon.png")
        self.setWindowIcon(QIcon(icon_path))

        # Variable to track window frame visibility
        self.frame_visible = False
    
        #Add AddMainWidget for main layout
        self.AddMainWidget(layout)

        # Set central widget
        self.setCentralWidget(central_widget)

        # Variables to track mouse click position
        self.dragging = False
        self.offset = QPoint()

        # Variables to track mouse position for resizing
        self.resize_origin = None
        self.resizing = False

        # Set initial stylesheet
        self.update_stylesheet()
        self.load_config()

        self.updateTextStyle()

        # Create a QTimer for periodic updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.fps = 5  # Set your desired frame rate in frames per second
        self.timer.start(int(1000 / self.fps))  # Timer interval in milliseconds
        self.cnt = 0
    
    #Add AddMainWidget for main layout
    def AddMainWidget(self,layout):
        # Main clock label and font size
        self.Main_label = QLabel("Clock", self)
        self.font_size = 300
        
        # Create a button to adjust window size and label size
        self.adjust_size_button = QPushButton("Adjust Size", self)
        self.adjust_size_button.setMouseTracking(True)  # Enable mouse tracking for continuous tracking
        self.adjust_size_button.installEventFilter(self)  # Install event filter to track mouse events
        self.adjust_size_button.setStyleSheet("font-size: 16px; color: #FFFFFF; background-color: #8D99AE;")

        # Button to change clock text color
        self.change_color_button = QPushButton("Change Color", self)
        self.change_color_button.setStyleSheet("font-size: 16px; color: #FFFFFF; background-color: #8D99AE;")
        self.change_color_button.pressed.connect(self.change_color_callback)

        # Create close button
        self.close_button = QPushButton("X", self)
        self.close_button.setStyleSheet("font-size: 16px; color: white; background-color: red;")
        self.close_button.pressed.connect(self.close_window)

        # Add the label to the layout
        layout.addWidget(self.Main_label)

        # Add buttons to the layout
        layout.addWidget(self.close_button, alignment=Qt.AlignTop | Qt.AlignRight)
        layout.addWidget(self.adjust_size_button, alignment=Qt.AlignTop | Qt.AlignRight)
        layout.addWidget(self.change_color_button, alignment=Qt.AlignTop | Qt.AlignRight)

    def change_color_callback(self):
        # Change clock text color on button press
        self.color_index += 1
        if self.color_index >= len(self.color_list):
            self.color_index = 0
        self.updateTextStyle()
        self.save_config()

    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and sets _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            # Use the current working directory for development or non-PyInstaller runs
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def updateTextStyle(self):
        # Update the style sheet for the clock label based on color and font size
        self.Main_label.setStyleSheet(f"font-size: {self.font_size}px; color: {self.color_list[self.color_index]};")

    def load_config(self):
        # Load configuration settings from the JSON config file
        try:
            with open(EzClock.CONFIG_FILE, 'r') as config_file:
                config = json.load(config_file)
                font_size = config.get('font_size', 24)
                window_size = config.get('window_size', {'width': 400, 'height': 300})
                pos = config.get('pos', [100, 100])
                frame_visible = config.get("visible", True)
                color_index = config.get("color_index", 0)
                self.move(pos[0], pos[1])
                self.frame_visible = frame_visible
                self.color_index = color_index
                self.font_size = font_size
                self.updateTextStyle()
                # Set window size
                self.setGeometry(100, 100, window_size['width'], window_size['height'])

        except FileNotFoundError:
            pass  # Config file doesn't exist, use default values

    def save_config(self):
        # Save the current configuration settings to the JSON config file
        config = {
            'font_size': self.font_size,
            'window_size': {'width': self.width(), 'height': self.height()},
            'pos': [self.pos().x(), self.pos().y()],
            'visible': self.frame_visible,
            'color_index': self.color_index
        }
        with open(EzClock.CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file)

    def resizeEvent(self, event):
        # Save the configuration when the window is resized
        self.save_config()
        super().resizeEvent(event)

    def eventFilter(self, source, event):
        # Event filter to handle mouse events for resizing
        if source == self.adjust_size_button:
            if event.type() == QEvent.MouseButtonPress:
                # Start resizing when the mouse button is pressed
                self.resize_origin = event.globalPos()
                size = self.size()
                self.resize_origin_width = size.width()
                self.resize_origin_height = size.height()
                self.resizing = True
            elif event.type() == QEvent.MouseMove and self.resizing:
                # Adjust window size and font size during resizing
                new_width = max(1, event.globalX() - self.resize_origin.x() + self.resize_origin_width)
                new_height = max(1, event.globalY() - self.resize_origin.y() + self.resize_origin_height)
                self.setGeometry(self.x(), self.y(), new_width, new_height)
                font_size = int(min(new_height, new_width) * 0.5)
                font_size = max(font_size, 1)
                self.font_size = font_size
                self.updateTextStyle()
                self.font_size = font_size
            elif event.type() == QEvent.MouseButtonRelease and self.resizing:
                # Stop resizing when the mouse button is released
                self.resizing = False

        return super().eventFilter(source, event)

    def mousePressEvent(self, event):
        # Handle mouse press to enable window dragging
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        # Handle mouse move to move the window
        if self.dragging:
            self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        # Handle mouse release to stop window dragging
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def mouseDoubleClickEvent(self, event):
        # Handle double-click to toggle window frame visibility
        self.frame_visible = not self.frame_visible
        self.update_stylesheet()

    def update_stylesheet(self):
        # Update window stylesheet based on frame visibility
        if self.frame_visible:
            self.setStyleSheet("QMainWindow {border: 4px solid white;}")
            self.close_button.show()
            self.adjust_size_button.show()
            self.change_color_button.show()
        else:
            self.setStyleSheet("QMainWindow {}")
            self.close_button.hide()
            self.adjust_size_button.hide()
            self.change_color_button.hide()

    def update_frame(self):
        # Update the clock label text with the current time
        current_time = QTime.currentTime().toString("hh:mm")
        print(current_time)
        self.Main_label.setText(f"{current_time}")

    def close_window(self):
        # Close the window when the close button is clicked
        self.close()

if __name__ == "__main__":
    # Create and run the application
    app = QApplication(sys.argv)
    window = EzClock()
    window.show()
    sys.exit(app.exec_())
