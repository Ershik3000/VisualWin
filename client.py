import sys, os, importlib
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QSize


#---------------------
# я не буду тут подсказывать это код вообще лучше не трогать он хрупкий
#---------------------
if hasattr(sys, 'frozen'):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(__file__)

meipass = getattr(sys, '_MEIPASS', base_dir)
config_path = os.path.join(base_dir, 'config.cfg')

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

def ensure_config_exists():
    if not os.path.exists(config_path):
        save_config(theme='dark', font='default')

def p(*a):
    x = os.path.join(base_dir, *a)
    if os.path.exists(x):
        return x
    x = os.path.join(meipass, *a)
    return x if os.path.exists(x) else os.path.join(*a)

def rp(pm, r):
    s = pm.size(); rp = QPixmap(s); rp.fill(Qt.GlobalColor.transparent)
    pt = QPainter(rp); pt.setRenderHint(QPainter.RenderHint.Antialiasing)
    pa = QPainterPath(); pa.addRoundedRect(0,0,s.width(),s.height(),r,r)
    pt.setClipPath(pa); pt.drawPixmap(0,0,pm); pt.end(); return rp

def get_font():
    config = load_config()
    if config.get('font') == 'mine':
        font_path = p('ttf', 'mine.ttf')
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    return QFont(families[0])
    return QFont("Segoe UI")

class VisualWinWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ensure_config_exists()
        config = load_config()
        self.theme = config.get('theme', 'dark')
        self.setWindowTitle("VisualWin")
        self.setGeometry(100, 100, 900, 600)
        self.setMinimumSize(800, 500)
        icon_path = p("icon", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.other_window = None
        self._init_ui()

    def _init_ui(self):
        if self.theme == 'white':
            bg = '#f5f5f5'; text = '#000000'; sub = '#666666'; card_bg = '#ffffff'
            btn_bg = '#000000'; btn_text = '#ffffff'; logo_name = 'logow.png'
            settings_icon = 'settingsw.png'; arrow_icon = 'rightarrowb.png'
            hover_color = '#e0e0e0'
        elif self.theme == 'purple':
            bg = '#0d0d1a'; text = '#ffffff'; sub = '#8b8ba0'; card_bg = '#1a1a35'
            btn_bg = '#6a0dad'; btn_text = '#ffffff'; logo_name = 'logo.png'
            settings_icon = 'settings.png'; arrow_icon = 'rightarrowb.png'
            hover_color = '#4a0080'
        else:
            bg = '#0a0a0a'; text = '#ffffff'; sub = '#8b949e'; card_bg = '#1a1a1a'
            btn_bg = '#ffffff'; btn_text = '#000000'; logo_name = 'logo.png'
            settings_icon = 'settings.png'; arrow_icon = 'rightarrow.png'
            hover_color = '#cccccc'

        base_font = get_font()

        self.setStyleSheet(f"""
            QWidget#central {{ background-color: {bg}; }}
            QLabel#title {{ color: {text}; font-size: 24px; font-weight: 700; }}
            QLabel#subtitle {{ color: {sub}; font-size: 13px; }}
            QLabel#cardTitle {{ color: {text}; font-size: 19px; font-weight: 600; }}
            QLabel#cardSub {{ color: {sub}; font-size: 12px; }}
            QLabel#cardDesc {{ color: {sub}; font-size: 12px; }}
        """)

        central_widget = QWidget()
        central_widget.setObjectName("central")
        self.setCentralWidget(central_widget)
        root = QVBoxLayout(central_widget)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)
        root.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        header = QHBoxLayout()
        header.setSpacing(12)
        header.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        logo_path = p("icon", logo_name)
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label = QLabel()
            logo_label.setPixmap(rp(logo_pixmap, 12))
            logo_label.setFixedSize(48, 48)
            header.addWidget(logo_label)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        title_label = QLabel("VisualWin")
        title_label.setObjectName("title")
        title_label.setFont(base_font)
        title_layout.addWidget(title_label)
        subtitle_label = QLabel("Клиент софтов")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setFont(base_font)
        title_layout.addWidget(subtitle_label)
        header.addLayout(title_layout)
        header.addStretch()

        settings_btn = QPushButton()
        settings_btn.setFixedSize(32, 32)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_icon_path = p("icon", settings_icon)
        if os.path.exists(settings_icon_path):
            settings_btn.setIcon(QIcon(settings_icon_path))
            settings_btn.setIconSize(QSize(20, 20))
        else:
            settings_btn.setText("⚙")
        settings_btn.setStyleSheet(f"QPushButton {{ background-color: transparent; border: none; }} QPushButton:hover {{ background-color: {hover_color}; border-radius: 6px; }}")
        settings_btn.clicked.connect(self.open_settings)
        header.addWidget(settings_btn, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        root.addLayout(header)

        card = QFrame()
        card.setFixedSize(340, 240)
        card.setStyleSheet(f"background-color: {card_bg}; border: none; border-radius: 16px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 15, 20, 14)
        card_layout.setSpacing(4)

        card_top = QHBoxLayout()
        card_top.setSpacing(14)
        card_top.setAlignment(Qt.AlignmentFlag.AlignTop)

        cs2_path = p("icon", "cs2.jpg")
        pixmap = QPixmap(cs2_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            pixmap = rp(pixmap, 14)
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setFixedSize(64, 64)
            image_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            card_top.addWidget(image_label)

        card_text = QVBoxLayout()
        card_text.setSpacing(2)
        card_text.setContentsMargins(0, 0, 0, 0)
        card_text.setAlignment(Qt.AlignmentFlag.AlignTop)

        game_title = QLabel("Counter-Strike 2")
        game_title.setObjectName("cardTitle")
        game_title.setFont(base_font)
        game_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        card_text.addWidget(game_title)

        game_sub = QLabel("internal/external, legit")
        game_sub.setObjectName("cardSub")
        game_sub.setFont(base_font)
        game_sub.setAlignment(Qt.AlignmentFlag.AlignLeft)
        card_text.addWidget(game_sub)

        card_top.addLayout(card_text)
        card_top.addStretch()
        card_layout.addLayout(card_top)

        desc_label = QLabel("Софт для Counter-Strike 2 для легитной игры, не детектится.\nПрисутствуют: Aimbot и Smooth.\nVisuals: ESP, Chams, Skeleton, Weapon.\nMisc: FOV, Bunnyhop, Radar hack, Anti-Flash.\nSounds: Headshot sound.\nWorld: particle snow/rain.")
        desc_label.setObjectName("cardDesc")
        desc_label.setWordWrap(True)
        desc_label.setFont(base_font)
        card_layout.addWidget(desc_label)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        action_btn = QPushButton("Перейти  ")
        action_btn.setFixedSize(100, 32)
        action_btn.setFont(base_font)
        action_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        action_btn.setStyleSheet(f"QPushButton {{ background-color: {btn_bg}; color: {btn_text}; border: none; border-radius: 8px; padding: 0 6px 0 2px; font-weight: bold; }} QPushButton:hover {{ background-color: {hover_color}; }}")
        arrow_path = p("icon", arrow_icon)
        if os.path.exists(arrow_path):
            action_btn.setIcon(QIcon(arrow_path))
            action_btn.setIconSize(action_btn.size() * 0.5)
        action_btn.clicked.connect(self.go_to_cs2)
        bottom_layout.addWidget(action_btn)
        card_layout.addLayout(bottom_layout)
        root.addWidget(card)
        root.addStretch()

    def go_to_cs2(self):
        try:
            cs2_module = importlib.import_module('cs2')
            cs2_window_class = getattr(cs2_module, 'DetailWindow')
            self.other_window = cs2_window_class()
            self.other_window.show()
            self.close()
        except:
            pass

    def open_settings(self):
        try:
            settings_module = importlib.import_module('settings')
            settings_window_class = getattr(settings_module, 'SettingsWindow')
            self.other_window = settings_window_class()
            self.other_window.show()
            self.close()
        except:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = VisualWinWindow()
    window.show()
    sys.exit(app.exec())