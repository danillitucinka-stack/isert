import sys
import os
import json
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QProgressBar, QMenu, QAction, QSystemTrayIcon, QPushButton, QDialog,
    QFormLayout, QComboBox, QColorDialog, QSpinBox, QCheckBox, QMessageBox,
    QFrame, QGridLayout
)
from PyQt5.QtCore import QTimer, Qt, QPoint, QRect, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QCursor
import psutil
import datetime

# Настройка логирования для отладки
logging.basicConfig(filename='widget.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Config:
    """
    Класс для управления конфигурацией виджета.
    Сохраняет настройки в JSON файл.
    """
    def __init__(self):
        self.config_file = 'config.json'
        self.default_config = {
            'position': {'x': 100, 'y': 100},
            'theme': 'cyberpunk',
            'font_family': 'Consolas',
            'font_size_clock': 24,
            'font_size_stats': 10,
            'font_size_notes': 10,
            'text_color': '#00ffcc',
            'background_alpha': 0.5,
            'auto_save_notes': True,
            'show_cpu': True,
            'show_ram': True,
            'show_disk': True,
            'show_battery': True,
            'update_interval_clock': 1000,
            'update_interval_stats': 2000,
            'minimize_to_tray': True,
            'show_notes': True
        }
        self.config = self.load_config()

    def load_config(self):
        """
        Загружает конфигурацию из файла.
        Если файл не существует, использует значения по умолчанию.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Объединяем с дефолтными значениями на случай новых настроек
                    self.default_config.update(loaded)
                    return self.default_config
            else:
                return self.default_config.copy()
        except Exception as e:
            logging.error(f"Ошибка загрузки конфигурации: {e}")
            return self.default_config.copy()

    def save_config(self):
        """
        Сохраняет текущую конфигурацию в файл.
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error(f"Ошибка сохранения конфигурации: {e}")

    def get(self, key):
        """
        Получает значение настройки по ключу.
        """
        return self.config.get(key, self.default_config.get(key))

    def set(self, key, value):
        """
        Устанавливает значение настройки.
        """
        self.config[key] = value
        self.save_config()

class SettingsDialog(QDialog):
    """
    Диалог настроек для изменения параметров виджета.
    """
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Настройки виджета")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """
        Инициализация интерфейса диалога настроек.
        """
        layout = QFormLayout()

        # Выбор темы
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['cyberpunk', 'minimalist', 'dark'])
        self.theme_combo.setCurrentText(self.config.get('theme'))
        layout.addRow("Тема:", self.theme_combo)

        # Шрифт для часов
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(['Consolas', 'Segoe UI Semibold', 'Arial'])
        self.font_family_combo.setCurrentText(self.config.get('font_family'))
        layout.addRow("Шрифт:", self.font_family_combo)

        self.font_size_clock_spin = QSpinBox()
        self.font_size_clock_spin.setRange(12, 48)
        self.font_size_clock_spin.setValue(self.config.get('font_size_clock'))
        layout.addRow("Размер шрифта часов:", self.font_size_clock_spin)

        # Цвет текста
        self.color_button = QPushButton("Выбрать цвет")
        self.color_button.clicked.connect(self.choose_color)
        layout.addRow("Цвет текста:", self.color_button)

        # Прозрачность фона
        self.alpha_spin = QSpinBox()
        self.alpha_spin.setRange(0, 100)
        self.alpha_spin.setValue(int(self.config.get('background_alpha') * 100))
        layout.addRow("Прозрачность фона (%):", self.alpha_spin)

        # Интервалы обновления
        self.update_clock_spin = QSpinBox()
        self.update_clock_spin.setRange(500, 5000)
        self.update_clock_spin.setValue(self.config.get('update_interval_clock'))
        layout.addRow("Интервал часов (мс):", self.update_clock_spin)

        self.update_stats_spin = QSpinBox()
        self.update_stats_spin.setRange(1000, 10000)
        self.update_stats_spin.setValue(self.config.get('update_interval_stats'))
        layout.addRow("Интервал статистики (мс):", self.update_stats_spin)

        # Чекбоксы для отображения элементов
        self.show_cpu_check = QCheckBox()
        self.show_cpu_check.setChecked(self.config.get('show_cpu'))
        layout.addRow("Показывать CPU:", self.show_cpu_check)

        self.show_ram_check = QCheckBox()
        self.show_ram_check.setChecked(self.config.get('show_ram'))
        layout.addRow("Показывать RAM:", self.show_ram_check)

        self.show_disk_check = QCheckBox()
        self.show_disk_check.setChecked(self.config.get('show_disk'))
        layout.addRow("Показывать диск:", self.show_disk_check)

        self.show_battery_check = QCheckBox()
        self.show_battery_check.setChecked(self.config.get('show_battery'))
        layout.addRow("Показывать батарею:", self.show_battery_check)

        self.minimize_tray_check = QCheckBox()
        self.minimize_tray_check.setChecked(self.config.get('minimize_to_tray'))
        layout.addRow("Сворачивать в трей:", self.minimize_tray_check)

        # Кнопки
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addRow(buttons_layout)

        self.setLayout(layout)

    def choose_color(self):
        """
        Выбор цвета текста через диалог.
        """
        color = QColorDialog.getColor(QColor(self.config.get('text_color')), self)
        if color.isValid():
            self.config.set('text_color', color.name())

    def save_settings(self):
        """
        Сохранение настроек и закрытие диалога.
        """
        self.config.set('theme', self.theme_combo.currentText())
        self.config.set('font_family', self.font_family_combo.currentText())
        self.config.set('font_size_clock', self.font_size_clock_spin.value())
        self.config.set('background_alpha', self.alpha_spin.value() / 100.0)
        self.config.set('update_interval_clock', self.update_clock_spin.value())
        self.config.set('update_interval_stats', self.update_stats_spin.value())
        self.config.set('show_cpu', self.show_cpu_check.isChecked())
        self.config.set('show_ram', self.show_ram_check.isChecked())
        self.config.set('show_disk', self.show_disk_check.isChecked())
        self.config.set('show_battery', self.show_battery_check.isChecked())
        self.config.set('minimize_to_tray', self.minimize_tray_check.isChecked())
        self.accept()

class StatsHistory:
    """
    Класс для хранения истории статистических данных.
    Позволяет отслеживать изменения во времени.
    """
    def __init__(self, max_points=50):
        self.max_points = max_points
        self.cpu_history = []
        self.ram_history = []
        self.disk_history = []

    def add_cpu(self, value):
        """
        Добавление значения CPU в историю.
        """
        self.cpu_history.append(value)
        if len(self.cpu_history) > self.max_points:
            self.cpu_history.pop(0)

    def add_ram(self, value):
        """
        Добавление значения RAM в историю.
        """
        self.ram_history.append(value)
        if len(self.ram_history) > self.max_points:
            self.ram_history.pop(0)

    def add_disk(self, value):
        """
        Добавление значения диска в историю.
        """
        self.disk_history.append(value)
        if len(self.disk_history) > self.max_points:
            self.disk_history.pop(0)

    def get_cpu_avg(self):
        """
        Получение среднего значения CPU за последние точки.
        """
        if self.cpu_history:
            return sum(self.cpu_history) / len(self.cpu_history)
        return 0

    def get_ram_avg(self):
        """
        Получение среднего значения RAM за последние точки.
        """
        if self.ram_history:
            return sum(self.ram_history) / len(self.ram_history)
        return 0

    def get_disk_avg(self):
        """
        Получение среднего значения диска за последние точки.
        """
        if self.disk_history:
            return sum(self.disk_history) / len(self.disk_history)
        return 0

class NetworkMonitor:
    """
    Класс для мониторинга сетевой активности.
    """
    def __init__(self):
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self.last_time = datetime.datetime.now()

    def get_network_stats(self):
        """
        Получение статистики сети: скорость отправки и приема.
        """
        try:
            net_io = psutil.net_io_counters()
            current_time = datetime.datetime.now()
            time_diff = (current_time - self.last_time).total_seconds()

            if time_diff > 0:
                sent_speed = (net_io.bytes_sent - self.last_bytes_sent) / time_diff / 1024  # KB/s
                recv_speed = (net_io.bytes_recv - self.last_bytes_recv) / time_diff / 1024  # KB/s
            else:
                sent_speed = 0
                recv_speed = 0

            self.last_bytes_sent = net_io.bytes_sent
            self.last_bytes_recv = net_io.bytes_recv
            self.last_time = current_time

            return sent_speed, recv_speed
        except Exception as e:
            logging.error(f"Ошибка получения сетевой статистики: {e}")
            return 0, 0

class TemperatureMonitor:
    """
    Класс для мониторинга температуры системы.
    """
    def __init__(self):
        try:
            self.sensors = psutil.sensors_temperatures() if hasattr(psutil, 'sensors_temperatures') else {}
        except Exception as e:
            logging.error(f"Ошибка инициализации датчиков температуры: {e}")
            self.sensors = {}

    def get_cpu_temp(self):
        """
        Получение температуры CPU.
        """
        try:
            if 'coretemp' in self.sensors:
                return self.sensors['coretemp'][0].current
            elif 'cpu_thermal' in self.sensors:
                return self.sensors['cpu_thermal'][0].current
            else:
                return None
        except Exception as e:
            logging.error(f"Ошибка получения температуры: {e}")
            return None

class HUDWidget(QWidget):
    """
    Основной класс виджета HUD.
    Отображает часы, заметки и статистику в стиле HUD.
    """
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.drag_position = None
        self.tray_icon = None
        self.theme_color = '#00ffcc'
        self.init_window()
        self.init_ui()
        self.init_timers()
        self.init_tray()
        self.load_position()
        self.apply_theme()

    def init_window(self):
        """
        Инициализация параметров окна.
        """
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 600)  # Увеличенный размер для HUD
        self.setWindowTitle("HUD Widget")

    def init_ui(self):
        """
        Инициализация пользовательского интерфейса.
        """
        # Головний контейнер
        self.container = QFrame(self)
        self.container.setStyleSheet("""
            background-color: rgba(15, 23, 42, 200);
            border-radius: 20px;
            border: 1px solid #00ffcc;
        """)
        self.container.setFixedSize(400, 600)

        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Зверху — годинник (великий, центрований)
        self.clock_label = QLabel("00:00:00")
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.clock_label)

        # Посередині — область статистики з QGridLayout
        self.stats_grid = QGridLayout()
        self.stats_grid.setHorizontalSpacing(10)
        self.stats_grid.setVerticalSpacing(10)

        # CPU
        self.cpu_label = QLabel("CPU:")
        self.cpu_label.setStyleSheet("color: #00ffcc;")
        self.stats_grid.addWidget(self.cpu_label, 0, 0)

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(0)
        self.cpu_bar.setFixedHeight(10)
        self.cpu_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                text-align: center;
                background-color: #111;
            }
            QProgressBar::chunk {
                background-color: #00ffcc;
                border-radius: 5px;
            }
        """)
        self.stats_grid.addWidget(self.cpu_bar, 0, 1)

        self.cpu_value_label = QLabel("0%")
        self.cpu_value_label.setStyleSheet("color: #00ffcc;")
        self.stats_grid.addWidget(self.cpu_value_label, 0, 2)

        # RAM
        self.ram_label = QLabel("RAM:")
        self.ram_label.setStyleSheet("color: #00ffcc;")
        self.stats_grid.addWidget(self.ram_label, 1, 0)

        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setValue(0)
        self.ram_bar.setFixedHeight(10)
        self.ram_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                text-align: center;
                background-color: #111;
            }
            QProgressBar::chunk {
                background-color: #00ffcc;
                border-radius: 5px;
            }
        """)
        self.stats_grid.addWidget(self.ram_bar, 1, 1)

        self.ram_value_label = QLabel("0%")
        self.ram_value_label.setStyleSheet("color: #00ffcc;")
        self.stats_grid.addWidget(self.ram_value_label, 1, 2)

        self.layout.addLayout(self.stats_grid)

        # Знизу — мережеві дані та нотатки
        self.network_label = QLabel("Network: N/A")
        self.network_label.setStyleSheet("color: #00ffcc;")
        self.layout.addWidget(self.network_label)

        self.temp_label = QLabel("Temp: N/A")
        self.temp_label.setStyleSheet("color: #00ffcc;")
        self.layout.addWidget(self.temp_label)

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(120)
        self.notes_edit.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.5);
            color: #00ffcc;
            border: none;
            border-radius: 10px;
        """)
        self.layout.addWidget(self.notes_edit)

        # Загрузка заметок
        self.load_notes()

        # Подключение сигналов
        self.notes_edit.textChanged.connect(self.save_notes)

    def init_timers(self):
        """
        Инициализация таймеров для обновления данных.
        """
        self.timer_clock = QTimer()
        self.timer_clock.timeout.connect(self.update_clock)

        self.timer_stats = QTimer()
        self.timer_stats.timeout.connect(self.update_stats)

        self.timer_network = QTimer()
        self.timer_network.timeout.connect(self.update_network)

        self.timer_temp = QTimer()
        self.timer_temp.timeout.connect(self.update_temperature)

        self.start_timers()

    def start_timers(self):
        """
        Запуск таймеров с интервалами из конфигурации.
        """
        self.timer_clock.start(self.config.get('update_interval_clock'))
        self.timer_stats.start(self.config.get('update_interval_stats'))
        self.timer_network.start(3000)
        self.timer_temp.start(5000)

    def init_tray(self):
        """
        Инициализация иконки в системном трее.
        """
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon(QPixmap(32, 32)))  # Простая иконка
            self.tray_icon.setToolTip("HUD Widget")

            tray_menu = QMenu()
            show_action = QAction("Показать", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)

            hide_action = QAction("Скрыть", self)
            hide_action.triggered.connect(self.hide)
            tray_menu.addAction(hide_action)

            quit_action = QAction("Выход", self)
            quit_action.triggered.connect(QApplication.quit)
            tray_menu.addAction(quit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()

    def apply_theme(self):
        """
        Применение темы.
        """
        font_family = self.config.get('font_family')
        text_color = self.theme_color

        # Стиль для часов
        clock_font = QFont(font_family, self.config.get('font_size_clock'), QFont.Bold)
        self.clock_label.setFont(clock_font)
        self.clock_label.setStyleSheet(f"color: {text_color};")

        # Стиль для статистики
        stats_font = QFont(font_family, self.config.get('font_size_stats'))
        self.cpu_label.setFont(stats_font)
        self.ram_label.setFont(stats_font)
        self.cpu_value_label.setFont(stats_font)
        self.ram_value_label.setFont(stats_font)

        # Стиль для заметок
        notes_font = QFont(font_family, self.config.get('font_size_notes'))
        self.notes_edit.setFont(notes_font)

    def update_clock(self):
        """
        Обновление отображения времени.
        """
        try:
            now = datetime.datetime.now()
            self.clock_label.setText(now.strftime("%H:%M:%S"))
        except Exception as e:
            logging.error(f"Ошибка обновления часов: {e}")

    def update_stats(self):
        """
        Обновление системной статистики.
        """
        try:
            if self.config.get('show_cpu'):
                cpu = psutil.cpu_percent(interval=0.1)
                self.cpu_bar.setValue(int(cpu))
                self.cpu_value_label.setText(f"{cpu:.1f}%")

            if self.config.get('show_ram'):
                ram = psutil.virtual_memory()
                self.ram_bar.setValue(int(ram.percent))
                self.ram_value_label.setText(f"{ram.percent:.1f}%")
        except Exception as e:
            logging.error(f"Ошибка обновления статистики: {e}")

    def update_network(self):
        """
        Обновление сетевой статистики.
        """
        try:
            net_io = psutil.net_io_counters()
            sent = net_io.bytes_sent / 1024 / 1024  # MB
            recv = net_io.bytes_recv / 1024 / 1024  # MB
            self.network_label.setText(f"Network: {sent:.1f} MB ↑ {recv:.1f} MB ↓")
        except Exception as e:
            logging.error(f"Ошибка обновления сети: {e}")
            self.network_label.setText("Network: N/A")

    def update_temperature(self):
        """
        Обновление температуры.
        """
        try:
            sensors = psutil.sensors_temperatures()
            if sensors:
                for name, entries in sensors.items():
                    if 'coretemp' in name or 'cpu' in name:
                        temp = entries[0].current
                        self.temp_label.setText(f"Temp: {temp:.1f}°C")
                        return
            self.temp_label.setText("Temp: N/A")
        except Exception as e:
            logging.error(f"Ошибка обновления температуры: {e}")
            self.temp_label.setText("Temp: N/A")

    def load_notes(self):
        """
        Загрузка заметок из файла.
        """
        try:
            if os.path.exists("notes.txt"):
                with open("notes.txt", "r", encoding="utf-8") as f:
                    self.notes_edit.setPlainText(f.read())
        except Exception as e:
            logging.error(f"Ошибка загрузки заметок: {e}")

    def save_notes(self):
        """
        Сохранение заметок в файл.
        """
        if not self.config.get('auto_save_notes'):
            return
        try:
            with open("notes.txt", "w", encoding="utf-8") as f:
                f.write(self.notes_edit.toPlainText())
        except Exception as e:
            logging.error(f"Ошибка сохранения заметок: {e}")

    def save_position(self):
        """
        Сохранение текущей позиции виджета.
        """
        pos = self.pos()
        self.config.set('position', {'x': pos.x(), 'y': pos.y()})

    def load_position(self):
        """
        Загрузка сохраненной позиции виджета.
        """
        pos = self.config.get('position')
        self.move(pos['x'], pos['y'])

    def show_settings(self):
        """
        Отображение диалога настроек.
        """
        dialog = SettingsDialog(self.config, self)
        if dialog.exec_():
            self.apply_theme()
            self.start_timers()

    def mousePressEvent(self, event):
        """
        Обработка нажатия мыши для перетаскивания.
        """
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        Обработка движения мыши для перетаскивания.
        """
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def closeEvent(self, event):
        """
        Обработка закрытия виджета.
        """
        self.save_position()
        self.save_notes()
        if self.tray_icon and self.config.get('minimize_to_tray'):
            event.ignore()
            self.hide()
            self.tray_icon.showMessage("HUD Widget", "Виджет свернут в трей", QSystemTrayIcon.Information, 2000)
        else:
            event.accept()

    def contextMenuEvent(self, event):
        """
        Обработка контекстного меню по правому клику.
        """
        menu = QMenu(self)

        notes_action = QAction("Сховати/Показати нотатки", self)
        notes_action.triggered.connect(self.toggle_notes)
        menu.addAction(notes_action)

        transparency_menu = menu.addMenu("Змінити прозорість")
        for alpha in [0.3, 0.5, 0.7, 0.9]:
            action = QAction(f"{int(alpha*100)}%", self)
            action.triggered.connect(lambda checked, a=alpha: self.set_transparency(a))
            transparency_menu.addAction(action)

        quit_action = QAction("Закрити", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        menu.exec_(event.globalPos())

    def toggle_notes(self):
        """
        Переключение видимости нотаток.
        """
        if self.notes_edit.isVisible():
            self.notes_edit.hide()
            self.config.set('show_notes', False)
        else:
            self.notes_edit.show()
            self.config.set('show_notes', True)

    def set_transparency(self, alpha):
        """
        Установка прозрачности контейнера.
        """
        self.container.setStyleSheet(f"""
            background-color: rgba(15, 23, 42, {int(alpha*255)});
            border-radius: 20px;
            border: 1px solid #00ffcc;
        """)
        self.config.set('background_alpha', alpha)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    widget = HUDWidget()
    widget.show()

    sys.exit(app.exec_())