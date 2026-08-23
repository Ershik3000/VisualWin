import sys
import os
import importlib
import requests
import subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QFont, QFontDatabase, QDesktopServices
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl, QSize

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(__file__)

meipass = getattr(sys, '_MEIPASS', base_dir)
config_path = os.path.join(base_dir, 'config.cfg')

def load_config():
    # сеты на деф
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

def p(*a):
    # хелп путей
    x = os.path.join(base_dir, *a)
    if os.path.exists(x):
        return x
    x = os.path.join(meipass, *a)
    return x if os.path.exists(x) else os.path.join(*a)

def rp(pm, r):
    s = pm.size()
    rp = QPixmap(s)
    rp.fill(Qt.GlobalColor.transparent)
    pt = QPainter(rp)
    pt.setRenderHint(QPainter.RenderHint.Antialiasing)
    pa = QPainterPath()
    pa.addRoundedRect(0, 0, s.width(), s.height(), r, r)
    pt.setClipPath(pa)
    pt.drawPixmap(0, 0, pm)
    pt.end()
    return rp

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
    return QFont("Segoe UI")  # стандарт шрифт 

class DownloadThread(QThread):
    pr = pyqtSignal(float, float)
    fn = pyqtSignal(bool, str)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        try:
            r = requests.get(self.url, stream=True, timeout=15)
            r.raise_for_status()
            total = float(r.headers.get('content-length', 0))
            downloaded = 0.0
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            with open(self.save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.pr.emit(downloaded, total)
            self.fn.emit(True, self.save_path)
        except Exception as e:
            self.fn.emit(False, str(e))

class DetailWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        config = load_config()
        self.theme = config.get('theme', 'dark')
        self.setWindowTitle("VisualWin")
        self.setGeometry(100, 100, 900, 600)
        self.setMinimumSize(800, 500)

        icon_path = p("icon", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.inj_dir = os.path.join(base_dir, 'inj')
        self.inj_exe = os.path.join(self.inj_dir, 'inj.exe')

        self.exter_dll_path = os.path.join(base_dir, 'dll', 'VisualWinExter.dll')
        self.inter_dll_path = os.path.join(base_dir, 'dll', 'VisualWinInter.dll')
        self.current_dll_path = None
        self.current_mode = None

        self._init_ui()
        self._check_dlls()

        self.download_thread = None
        self.cmd_process = None
        self.cmd_timer = None
        self.other_window = None

    def _init_ui(self):
        # нахуй заморачиватся везде в коде если все сразу прописал
        if self.theme == 'white':
            bg = '#f5f5f5'
            text = '#000000'
            sub = '#666666'
            logo_name = 'logow.png'
            settings_icon = 'settingsw.png'
            card_bg = '#ffffff'
            btn_bg = '#e0e0e0'
            btn_text = '#000000'
            hover_bg = '#d0d0d0'
        elif self.theme == 'purple':
            bg = '#0d0d1a'
            text = '#ffffff'
            sub = '#8b8ba0'
            logo_name = 'logo.png'
            settings_icon = 'settings.png'
            card_bg = '#1a1a35'
            btn_bg = '#2a1a4a'
            btn_text = '#ffffff'
            hover_bg = '#3a2a5a'
        else:  # черни
            bg = '#0a0a0a'
            text = '#ffffff'
            sub = '#8b949e'
            logo_name = 'logo.png'
            settings_icon = 'settings.png'
            card_bg = '#1a1a1a'
            btn_bg = '#2a2a2a'
            btn_text = '#ffffff'
            hover_bg = '#3a3a3a'

        base_font = get_font()

        self.setStyleSheet(f"""
            QWidget#central {{ background-color: {bg}; }}
            QLabel {{ border: none; }}
            QPushButton {{ border: none; }}
            QLabel#title {{ color: {text}; font-size: 24px; font-weight: 700; }}
            QLabel#subtitle {{ color: {sub}; font-size: 13px; }}
            QLabel#bigTitle {{ color: {text}; font-size: 36px; font-weight: 800; }}
            QLabel#modeTitle {{ color: {text}; font-size: 20px; font-weight: 700; }}
            QLabel#modeDesc {{ color: {sub}; font-size: 12px; }}
        """)

        central_widget = QWidget()
        central_widget.setObjectName("central")
        self.setCentralWidget(central_widget)

        self.root_layout = QVBoxLayout(central_widget)
        self.root_layout.setContentsMargins(24, 16, 24, 16)
        self.root_layout.setSpacing(8)
        self.root_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # шапочка
        header = QHBoxLayout()
        header.setSpacing(8)
        header.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        logo_path = p("icon", logo_name)
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label = QLabel()
            logo_label.setPixmap(rp(logo_pixmap, 10))
            logo_label.setFixedSize(40, 40)
            header.addWidget(logo_label)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)

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

        # батон настроек
        settings_btn = QPushButton()
        settings_btn.setFixedSize(28, 28)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_icon_path = p("icon", settings_icon)
        if os.path.exists(settings_icon_path):
            settings_btn.setIcon(QIcon(settings_icon_path))
            settings_btn.setIconSize(QSize(18, 18))
        else:
            settings_btn.setText("ошибка")  # хз если удалите иконку
            settings_btn.setStyleSheet(f"color: {sub}; font-size: 16px;")
        settings_btn.setStyleSheet(f"QPushButton {{ background-color: transparent; }} QPushButton:hover {{ background-color: {hover_bg}; border-radius: 4px; }}")
        settings_btn.clicked.connect(self.open_settings)
        header.addWidget(settings_btn)

        self.root_layout.addLayout(header)

        # заголовочек
        cs_layout = QHBoxLayout()
        cs_layout.addStretch()

        cs_label = QLabel("Counter-Strike 2")
        cs_label.setObjectName("bigTitle")
        cs_label.setFont(base_font)
        cs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cs_layout.addWidget(cs_label)
        cs_layout.addStretch()

        self.root_layout.addLayout(cs_layout)

        back_layout = QHBoxLayout()
        back_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        back_layout.setContentsMargins(0, 0, 0, 0)

        self.back_btn = QPushButton("Назад")
        self.back_btn.setFixedSize(70, 28)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setStyleSheet(f"QPushButton {{ background-color: transparent; color: {sub}; font-size: 13px; font-weight: 600; text-align: left; padding: 0; }} QPushButton:hover {{ color: {text}; }}")
        self.back_btn.setFont(base_font)
        self.back_btn.clicked.connect(self.go_back)
        back_layout.addWidget(self.back_btn)

        self.root_layout.addLayout(back_layout)

        # блокич экстернала
        exter_card = QFrame()
        exter_card.setFixedHeight(100)
        exter_card.setStyleSheet(f"background-color: {card_bg}; border-radius: 14px;")

        exter_layout = QVBoxLayout(exter_card)
        exter_layout.setContentsMargins(20, 8, 20, 8)
        exter_layout.setSpacing(0)

        exter_row = QHBoxLayout()
        exter_row.setSpacing(0)

        exter_title_layout = QVBoxLayout()
        exter_title_layout.setSpacing(0)

        exter_title = QLabel("External")
        exter_title.setObjectName("modeTitle")
        exter_title.setFont(base_font)
        exter_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        exter_title_layout.addWidget(exter_title)

        exter_desc = QLabel("Внешний чит, работает через отдельный процесс")
        exter_desc.setObjectName("modeDesc")
        exter_desc.setFont(base_font)
        exter_desc.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        exter_title_layout.addWidget(exter_desc)

        exter_row.addLayout(exter_title_layout)
        exter_row.addStretch()

        self.exter_btn = QPushButton("Скачать")
        self.exter_btn.setFixedSize(130, 34)
        self.exter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exter_btn.setFont(base_font)
        self.exter_btn.setStyleSheet(f"QPushButton {{ background-color: {btn_bg}; color: {btn_text}; border-radius: 8px; font-weight: bold; font-size: 13px; }} QPushButton:hover {{ background-color: {hover_bg}; }}")
        self.exter_btn.clicked.connect(lambda: self.on_mode_click('exter'))
        exter_row.addWidget(self.exter_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        exter_layout.addLayout(exter_row)
        self.root_layout.addWidget(exter_card)

        # бля я заебался это интернал блок
        inter_card = QFrame()
        inter_card.setFixedHeight(100)
        inter_card.setStyleSheet(f"background-color: {card_bg}; border-radius: 14px;")

        inter_layout = QVBoxLayout(inter_card)
        inter_layout.setContentsMargins(20, 8, 20, 8)
        inter_layout.setSpacing(0)

        inter_row = QHBoxLayout()
        inter_row.setSpacing(0)

        inter_title_layout = QVBoxLayout()
        inter_title_layout.setSpacing(0)

        inter_title = QLabel("Internal")
        inter_title.setObjectName("modeTitle")
        inter_title.setFont(base_font)
        inter_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        inter_title_layout.addWidget(inter_title)

        inter_desc = QLabel("Внутренний чит, работает через инжект в игру")
        inter_desc.setObjectName("modeDesc")
        inter_desc.setFont(base_font)
        inter_desc.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        inter_title_layout.addWidget(inter_desc)

        inter_row.addLayout(inter_title_layout)
        inter_row.addStretch()

        self.inter_btn = QPushButton("Скачать")
        self.inter_btn.setFixedSize(130, 34)
        self.inter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.inter_btn.setFont(base_font)
        self.inter_btn.setStyleSheet(f"QPushButton {{ background-color: {btn_bg}; color: {btn_text}; border-radius: 8px; font-weight: bold; font-size: 13px; }} QPushButton:hover {{ background-color: {hover_bg}; }}")
        self.inter_btn.clicked.connect(lambda: self.on_mode_click('inter'))
        inter_row.addWidget(self.inter_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        inter_layout.addLayout(inter_row)
        self.root_layout.addWidget(inter_card)

        # прогресс скачивания
        self.download_panel = QFrame()
        self.download_panel.setFixedHeight(0)
        self.download_panel.setStyleSheet(f"background-color: {bg}; border-radius: 8px;")
        self.download_panel.hide()

        panel_layout = QVBoxLayout(self.download_panel)
        panel_layout.setContentsMargins(16, 8, 16, 8)

        self.download_title = QLabel()
        self.download_title.setStyleSheet(f"color: {text}; font-size: 14px; font-weight: bold;")
        self.download_title.setFont(base_font)
        panel_layout.addWidget(self.download_title)

        self.download_info = QLabel()
        self.download_info.setStyleSheet(f"color: {sub}; font-size: 12px;")
        self.download_info.setFont(base_font)
        panel_layout.addWidget(self.download_info)

        self.root_layout.addWidget(self.download_panel)
        self.root_layout.addStretch()

    def show_panel(self, title, info):
        self.download_title.setText(title)
        self.download_info.setText(info)
        self.download_panel.setFixedHeight(70)
        self.download_panel.show()

    def close_panel(self):
        self.download_panel.hide()
        self.download_panel.setFixedHeight(0)

    def _check_dlls(self):
        # проверка есть ли дллка
        if os.path.exists(self.exter_dll_path):
            self.exter_btn.setText("Запустить")
        else:
            self.exter_btn.setText("Скачать")

        if os.path.exists(self.inter_dll_path):
            self.inter_btn.setText("Запустить")
        else:
            self.inter_btn.setText("Скачать")

    def _create_settings_xml(self):
        # я ебал эту хуйню
        try:
            os.makedirs(self.inj_dir, exist_ok=True)
            dll_path = self.current_dll_path if self.current_dll_path else ''
            dll_path_forward = dll_path.replace('\\', '/') if dll_path else ''

            # тут не менять не будет работать инжект
            xml_content = f'''<?xml version="1.0" encoding="utf-8"?>
<_x206A__x200F__x202D__x206B__x206C__x202A__x202E__x200F__x200F__x206F__x202D__x200E__x206A__x200E__x206C__x200B__x202C__x206F__x206B__x202A__x206A__x206C__x202B__x200C__x200F__x200D__x200C__x202C__x202A__x200B__x200D__x200D__x206B__x206C__x202C__x200D__x206A__x202B__x202B__x206F__x202E_ xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
  <LastUpdateCheck>2026-08-16T22:26:58.0106327+03:00</LastUpdateCheck>
  <Modules>
    <_x206A__x206F__x206B__x206A__x202B__x206E__x200C__x206F__x200F__x202A__x200B__x202E__x206E__x206E__x206B__x202C__x200F__x202D__x202B__x202B__x200F__x200B__x206D__x200F__x200C__x206F__x200F__x202D__x206F__x206A__x206F__x200E__x202C__x202C__x202B__x202A__x202C__x202B__x202A__x202A__x202E_>
      <Enable>true</Enable>
      <Export i:nil="true" />
      <Parameters i:nil="true" />
      <Path>{dll_path_forward}</Path>
    </_x206A__x206F__x206B__x206A__x202B__x206E__x200C__x206F__x200F__x202A__x200B__x202E__x206E__x206E__x206B__x202C__x200F__x202D__x202B__x202B__x200F__x200B__x206D__x200F__x200C__x206F__x200F__x202D__x206F__x206A__x206F__x200E__x202C__x202C__x202B__x202A__x202C__x202B__x202A__x202A__x202E_>
  </Modules>
  <Options>
    <Advanced>
      <DisableExceptionSupport>false</DisableExceptionSupport>
      <DisableSEHValidation>false</DisableSEHValidation>
      <HideFromDebugger>false</HideFromDebugger>
      <ManualResolveImports>false</ManualResolveImports>
    </Advanced>
    <AutoInject>true</AutoInject>
    <Background1>DodgerBlue</Background1>
    <Background2>DeepSkyBlue</Background2>
    <CloseOnInject>false</CloseOnInject>
    <Delay>60</Delay>
    <DelayBetween>0</DelayBetween>
    <ErasePE>true</ErasePE>
    <HideModule>true</HideModule>
    <Method>4</Method>
    <Scramble>
      <CreateFakeDebugDirectory>false</CreateFakeDebugDirectory>
      <CreateNewEntryPoint>false</CreateNewEntryPoint>
      <InsertExtraSections>false</InsertExtraSections>
      <ModifyAssemblyCode>false</ModifyAssemblyCode>
      <ModifyImportTable>false</ModifyImportTable>
      <MoveRelocationTable>false</MoveRelocationTable>
      <RemoveDebugData>false</RemoveDebugData>
      <RemoveUselessData>false</RemoveUselessData>
      <RenameSections>false</RenameSections>
      <ScrambleHeaderFields>false</ScrambleHeaderFields>
      <ShiftSectionData>false</ShiftSectionData>
      <ShiftSectionMemory>false</ShiftSectionMemory>
      <StripSectionCharacteristics>false</StripSectionCharacteristics>
    </Scramble>
    <StealthInject>false</StealthInject>
    <TextColor>White</TextColor>
  </Options>
  <ProcessName>cs2.exe</ProcessName>
  <Warnings>
    <LdrpLoadDll>false</LdrpLoadDll>
    <ManualMap>false</ManualMap>
    <Scramble>false</Scramble>
  </Warnings>
</_x206A__x200F__x202D__x206B__x206C__x202A__x202E__x200F__x200F__x206F__x202D__x200E__x206A__x200E__x206C__x200B__x202C__x206F__x206B__x202A__x206A__x206C__x202B__x200C__x200F__x200D__x200C__x202C__x202A__x200B__x200D__x200D__x206B__x206C__x202C__x200D__x206A__x202B__x202B__x206F__x202E_>'''

            settings_path = os.path.join(self.inj_dir, 'settings.xml')
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
        except:
            pass  # пизда если не создалсс

    def on_mode_click(self, mode):
        self.current_mode = mode
        if mode == 'exter':
            self.current_dll_path = self.exter_dll_path
            if os.path.exists(self.exter_dll_path):
                self.start_launch_sequence()
            else:
                self.start_download('https://visualwin.cloudpub.ru/api/download_exter', self.exter_dll_path, 'External')
        else:  # inter
            self.current_dll_path = self.inter_dll_path
            if os.path.exists(self.inter_dll_path):
                self.start_launch_sequence()
            else:
                self.start_download('https://visualwin.cloudpub.ru/api/download_inter', self.inter_dll_path, 'Internal')

    def start_download(self, url, save_path, mode_name):
        self.show_panel("Скачивание", f"0.0/0.0M  Идет скачивание {mode_name} чита")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # загрузка в потоке отдельном как канава
        self.download_thread = DownloadThread(url, save_path)
        self.download_thread.pr.connect(self.update_progress)
        self.download_thread.fn.connect(self.download_finished)
        self.download_thread.start()

    def update_progress(self, downloaded, total):
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024) if total > 0 else 0
        mode_name = "External" if self.current_mode == 'exter' else "Internal"
        self.download_info.setText(f"{downloaded_mb:.1f}/{total_mb:.1f}M  Идет скачивание {mode_name} чита")

    def download_finished(self, success, message):
        if success:
            self.close_panel()
            self._check_dlls()
        else:
            # если ошибка будет пиздец
            self.download_info.setText(f"Ошибка: {message}")

    def start_launch_sequence(self):
        # варнингаем типа(это для того чтобы меньше был шанс детекта)
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Внимание!")
        msg_box.setText("Обязательно нажмите Нет при подтверждении прав администратора")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.button(QMessageBox.StandardButton.Ok).clicked.connect(self.launch_inj)
        msg_box.exec()

    def launch_inj(self):
        try:
            self.show_panel("Запуск чита", "Запускаем...")
            self._create_settings_xml()

            # крейтим батник для запуска(ебал extreminjector запускается c xml только через cmd)
            bat_path = os.path.join(self.inj_dir, 'run_inj.bat')
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write('@echo off\n')
                f.write('cd /d "%~dp0"\n')
                f.write('start "" /wait inj.exe\n')
                f.write('exit\n')

            self.cmd_process = subprocess.Popen(
                ['cmd.exe', '/c', bat_path],
                cwd=self.inj_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0
            )

            # запускаем кс2 бля не помню там вроде с ксго тоже самое
            QDesktopServices.openUrl(QUrl("steam://rungameid/730"))

            # таймим запуск
            self.cmd_timer = QTimer(self)
            self.cmd_timer.timeout.connect(self.check_cmd_finished)
            self.cmd_timer.start(500)
        except Exception as e:
            self.download_info.setText(f"Ошибка: {e}")

    def check_cmd_finished(self):
        if self.cmd_process and self.cmd_process.poll() is not None:
            if self.cmd_timer:
                self.cmd_timer.stop()
                self.cmd_timer = None
            self.show_panel("Готово", "Чит заинжекчен")

    def open_settings(self):
        # окно настроек открытие 
        try:
            settings_module = importlib.import_module('settings')
            settings_window_class = getattr(settings_module, 'SettingsWindow')
            self.other_window = settings_window_class()
            self.other_window.show()
            self.close()
        except Exception:
            pass  # игнор модуля

    def go_back(self):
        # возврат на главный экран
        try:
            client_module = importlib.import_module('client')
            client_window_class = getattr(client_module, 'VisualWinWindow')
            self.other_window = client_window_class()
            self.other_window.show()
            self.close()
        except Exception:
            pass

    def closeEvent(self, event):
        # очистка кэша перед закрытием
        if self.cmd_timer:
            self.cmd_timer.stop()
            self.cmd_timer = None
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()
            self.download_thread.wait(1000)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DetailWindow()
    window.show()
    sys.exit(app.exec())