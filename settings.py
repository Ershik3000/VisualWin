import sys, os, importlib
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtGui import QIcon, QPixmap, QFontDatabase, QFont
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve

# определение базы деректории для собраной хуйни
bd = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(__file__)
config_path = os.path.join(os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else bd, 'config.cfg')

def load_config():
    config = {'theme': 'dark', 'font': 'default'}
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        config[key.strip()] = value.strip()
    except:
        pass
    return config

def save_config(theme=None, font=None):
    config = load_config()
    if theme:
        config['theme'] = theme
    if font:
        config['font'] = font
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
    except:
        pass

def p(*a):
    x = os.path.join(bd, *a)
    return x if os.path.exists(x) else os.path.join(*a)

class ColorSquare(QFrame):
    def __init__(self, color, size=40, selected=False, parent=None):
        super().__init__(parent)
        self.color = color
        self.selected = selected
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # зачем блять дохуя повторять это
        if selected:
            border = '#ffffff' if color == '#0a0a0a' else '#000000'
            border_width = '3px'
        else:
            border = '#555555' if color != '#ffffff' else '#000000'
            border_width = '2px'
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: {border_width} solid {border};
                border-radius: 10px;
            }}
        """)

class FontButton(QPushButton):
    def __init__(self, text, selected=False, parent=None):
        super().__init__(text, parent)
        self.selected = selected
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#333333' if selected else 'transparent'};
                color: #ffffff;
                border: 2px solid {'#ffffff' if selected else '#555555'};
                border-radius: 8px;
                padding: 0 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                border: 2px solid #ffffff;
            }}
        """)

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        config = load_config()
        self.theme = config.get('theme', 'dark')
        self.font_choice = config.get('font', 'default')
        self.setWindowTitle("Настройки")
        self.setGeometry(100, 100, 900, 600)
        self.setMinimumSize(800, 500)
        icon_path = p("icon", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.other_window = None
        self._init_ui()

    def _init_ui(self):
        if self.theme == 'white':
            bg = '#f5f5f5'; text = '#000000'; sub = '#666666'
        elif self.theme == 'purple':
            bg = '#0d0d1a'; text = '#ffffff'; sub = '#8b8ba0'
        else:
            bg = '#0a0a0a'; text = '#ffffff'; sub = '#8b949e'

        self.setStyleSheet(f"QWidget#central {{ background-color: {bg}; }}")
        central_widget = QWidget()
        central_widget.setObjectName("central")
        self.setCentralWidget(central_widget)

        root = QVBoxLayout(central_widget)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)
        root.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        back_btn = QPushButton("Назад")
        back_btn.setFixedWidth(80)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet(f"QPushButton {{ background-color: transparent; border: none; color: {sub}; font-size: 14px; font-weight: 600; text-align: left; padding: 0; }} QPushButton:hover {{ color: {text}; }}")
        back_btn.clicked.connect(self.go_back)
        root.addWidget(back_btn)

        root.addSpacing(10)

        theme_label = QLabel("Тема")
        theme_label.setStyleSheet(f"color: {text}; font-size: 22px; font-weight: bold;")
        root.addWidget(theme_label)

        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(16)

        self.dark_square = ColorSquare('#0a0a0a', selected=(self.theme == 'dark'))
        self.dark_square.mousePressEvent = lambda e: self.select_theme('dark')
        colors_layout.addWidget(self.dark_square)

        self.white_square = ColorSquare('#ffffff', selected=(self.theme == 'white'))
        self.white_square.mousePressEvent = lambda e: self.select_theme('white')
        colors_layout.addWidget(self.white_square)

        self.purple_square = ColorSquare('#6a0dad', selected=(self.theme == 'purple'))
        self.purple_square.mousePressEvent = lambda e: self.select_theme('purple')
        colors_layout.addWidget(self.purple_square)

        colors_layout.addStretch()
        root.addLayout(colors_layout)

        root.addSpacing(20)

        font_label = QLabel("Шрифты")
        font_label.setStyleSheet(f"color: {text}; font-size: 22px; font-weight: bold;")
        root.addWidget(font_label)

        fonts_layout = QHBoxLayout()
        fonts_layout.setSpacing(16)

        self.default_font_btn = FontButton("Стандартный", selected=(self.font_choice == 'default'))
        self.default_font_btn.clicked.connect(lambda: self.select_font('default'))
        fonts_layout.addWidget(self.default_font_btn)

        self.mine_font_btn = FontButton("Mine", selected=(self.font_choice == 'mine'))
        self.mine_font_btn.clicked.connect(lambda: self.select_font('mine'))
        fonts_layout.addWidget(self.mine_font_btn)

        fonts_layout.addStretch()
        root.addLayout(fonts_layout)
        root.addStretch()

    def select_theme(self, theme):
        save_config(theme=theme)
        self.theme = theme
        # анимка перехода темы
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(150)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_out.finished.connect(lambda: self._recreate_ui())
        self.fade_out.start()

    def select_font(self, font):
        save_config(font=font)
        self.font_choice = font
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(150)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_out.finished.connect(lambda: self._recreate_ui())
        self.fade_out.start()

    def _recreate_ui(self):
        self._init_ui()
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(150)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_in.start()

    def go_back(self):
        try:
            client_module = importlib.import_module('client')
            client_window_class = getattr(client_module, 'VisualWinWindow')
            self.other_window = client_window_class()
            self.other_window.show()
            self.close()
        except:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())