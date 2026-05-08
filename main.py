import sys
import os
import json
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QTextEdit, QHBoxLayout,
    QPushButton, QMenu, QAction, QSystemTrayIcon, QDialog, QFormLayout,
    QComboBox, QColorDialog, QSpinBox, QCheckBox, QMessageBox
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
            'minimize_to_tray': True
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

class SystemWidget(QWidget):
    """
    Основной класс виджета системы.
    Отображает часы, заметки и статистику.
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
        try:
            self.apply_theme()
        except Exception as e:
            logging.error(f"Ошибка применения темы: {e}")

    def init_window(self):
        """
        Инициализация параметров окна.
        """
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(350, 500)  # Увеличенный размер для дополнительных элементов
        self.setWindowTitle("System Widget")

    def init_ui(self):
        """
        Инициализация пользовательского интерфейса.
        """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(self.layout)

        # Кнопка настроек
        self.settings_button = QPushButton("⚙")
        self.settings_button.setFixedSize(30, 30)
        self.settings_button.setStyleSheet("background-color: rgba(0,0,0,0.3); color: #00ffcc; border: none;")
        self.settings_button.clicked.connect(self.show_settings)
        self.layout.addWidget(self.settings_button, alignment=Qt.AlignRight)

        # Цифровые часы
        self.clock_label = QLabel("00:00:00")
        self.layout.addWidget(self.clock_label)

        # Поле для заметок
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(120)
        self.layout.addWidget(self.notes_edit)

        # Системные статистики
        self.stats_label = QLabel("Инициализация...")
        self.layout.addWidget(self.stats_label)

        # Загрузка заметок
        self.load_notes()

        # Подключение сигналов
        self.notes_edit.textChanged.connect(self.save_notes)
        self.notes_edit.focusOutEvent = self.on_notes_focus_out

    def init_timers(self):
        """
        Инициализация таймеров для обновления данных.
        """
        self.timer_clock = QTimer()
        self.timer_clock.timeout.connect(self.update_clock)

        self.timer_stats = QTimer()
        self.timer_stats.timeout.connect(self.update_stats)

        self.start_timers()

    def start_timers(self):
        """
        Запуск таймеров с интервалами из конфигурации.
        """
        self.timer_clock.start(self.config.get('update_interval_clock'))
        self.timer_stats.start(self.config.get('update_interval_stats'))

    def init_tray(self):
        """
        Инициализация иконки в системном трее.
        """
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon(QPixmap(32, 32)))  # Простая иконка
            self.tray_icon.setToolTip("System Widget")

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
        Применение темы из конфигурации.
        """
        font_family = self.config.get('font_family')
        text_color = self.theme_color
        alpha = self.config.get('background_alpha')

        # Стиль для часов
        clock_font = QFont(font_family, self.config.get('font_size_clock'), QFont.Bold)
        self.clock_label.setFont(clock_font)
        self.clock_label.setStyleSheet(f"color: {text_color};")

        # Стиль для заметок
        notes_font = QFont(font_family, self.config.get('font_size_notes'))
        self.notes_edit.setFont(notes_font)
        self.notes_edit.setStyleSheet(f"background-color: rgba(0, 0, 0, {alpha}); color: {text_color}; border: none;")

        # Стиль для статистики
        stats_font = QFont(font_family, self.config.get('font_size_stats'))
        self.stats_label.setFont(stats_font)
        self.stats_label.setStyleSheet(f"color: {text_color};")

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
            stats_text = ""

            if self.config.get('show_cpu'):
                cpu = psutil.cpu_percent(interval=0.1)
                stats_text += f"CPU: {cpu:.1f}%\n"

            if self.config.get('show_ram'):
                ram = psutil.virtual_memory()
                ram_gb = ram.used / (1024**3)
                stats_text += f"RAM: {ram.percent:.1f}% ({ram_gb:.1f} GB)\n"

            if self.config.get('show_disk'):
                disk = psutil.disk_usage('C:')
                disk_gb = disk.free / (1024**3)
                stats_text += f"Disk C: {disk_gb:.1f} GB free\n"

            if self.config.get('show_battery'):
                battery = psutil.sensors_battery()
                if battery:
                    stats_text += f"Battery: {battery.percent:.1f}% {'(Charging)' if battery.power_plugged else ''}\n"

            self.stats_label.setText(stats_text.strip())
        except Exception as e:
            logging.error(f"Ошибка обновления статистики: {e}")
            self.stats_label.setText("Ошибка получения статистики")

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
        # Сохранение заметок в файл
        if not self.config.get('auto_save_notes'):
            return
        try:
            with open("notes.txt", "w", encoding="utf-8") as f:
                f.write(self.notes_edit.toPlainText())
        except Exception as e:
            logging.error(f"Ошибка сохранения заметок: {e}")

    def on_notes_focus_out(self, event):
        # Автосохранение при потере фокуса
        self.save_notes()
        QTextEdit.focusOutEvent(self.notes_edit, event)

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
        if self.tray_icon and self.config.get('minimize_to_tray'):
            event.ignore()
            self.hide()
            self.tray_icon.showMessage("System Widget", "Виджет свернут в трей", QSystemTrayIcon.Information, 2000)
        else:
            event.accept()

    def contextMenuEvent(self, event):
        """
        Обработка контекстного меню по правому клику.
        """
        menu = QMenu(self)
        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)

        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        menu.exec_(event.globalPos())

# Дополнительные классы и функции для расширения функциональности

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

# Расширение класса SystemWidget дополнительными функциями

class ExtendedSystemWidget(SystemWidget):
    """
    Расширенная версия виджета с дополнительными функциями.
    """
    def __init__(self):
        super().__init__()
        self.stats_history = StatsHistory()
        self.network_monitor = NetworkMonitor()
        self.temp_monitor = TemperatureMonitor()
        self.init_extended_ui()
        self.init_extended_timers()
        try:
            self.apply_theme()
        except Exception as e:
            logging.error(f"Ошибка применения темы в ExtendedSystemWidget: {e}")

    def init_extended_ui(self):
        """
        Инициализация расширенного интерфейса.
        """
        # Полоски для CPU и RAM
        self.cpu_label = QLabel("CPU:")
        self.cpu_label.setFont(QFont(self.config.get('font_family'), 9))
        self.layout.addWidget(self.cpu_label)

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(0)
        self.cpu_bar.setFixedHeight(15)
        self.layout.addWidget(self.cpu_bar)

        self.ram_label = QLabel("RAM:")
        self.ram_label.setFont(QFont(self.config.get('font_family'), 9))
        self.layout.addWidget(self.ram_label)

        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setValue(0)
        self.ram_bar.setFixedHeight(15)
        self.layout.addWidget(self.ram_bar)

        # Добавление метки для сети
        self.network_label = QLabel("Network: 0 KB/s ↓ 0 KB/s ↑")
        self.network_label.setFont(QFont(self.config.get('font_family'), 9))
        self.network_label.setStyleSheet(f"color: {self.theme_color};")
        self.layout.addWidget(self.network_label)

        # Добавление метки для температуры
        self.temp_label = QLabel("Temp: N/A")
        self.temp_label.setFont(QFont(self.config.get('font_family'), 9))
        self.temp_label.setStyleSheet(f"color: {self.theme_color};")
        self.layout.addWidget(self.temp_label)

        # Добавление метки для истории
        self.history_label = QLabel("Avg CPU: 0% | Avg RAM: 0%")
        self.history_label.setFont(QFont(self.config.get('font_family'), 8))
        self.history_label.setStyleSheet(f"color: {self.theme_color};")
        self.layout.addWidget(self.history_label)

    def init_extended_timers(self):
        """
        Инициализация дополнительных таймеров.
        """
        self.timer_network = QTimer()
        self.timer_network.timeout.connect(self.update_network)
        self.timer_network.start(3000)  # Каждые 3 секунды

        self.timer_temp = QTimer()
        self.timer_temp.timeout.connect(self.update_temperature)
        self.timer_temp.start(5000)  # Каждые 5 секунд

        self.timer_notes_save = QTimer()
        self.timer_notes_save.timeout.connect(self.save_notes)
        self.timer_notes_save.start(30000)  # Автосохранение каждые 30 секунд

    def update_network(self):
        """
        Обновление сетевой статистики.
        """
        try:
            sent, recv = self.network_monitor.get_network_stats()
            self.network_label.setText(f"Network: {sent:.1f} KB/s ↑ {recv:.1f} KB/s ↓")
        except Exception as e:
            logging.error(f"Ошибка обновления сети: {e}")

    def update_temperature(self):
        """
        Обновление температуры.
        """
        try:
            temp = self.temp_monitor.get_cpu_temp()
            if temp is not None:
                self.temp_label.setText(f"Temp: {temp:.1f}°C")
            else:
                self.temp_label.setText("Temp: N/A")
        except Exception as e:
            logging.error(f"Ошибка обновления температуры: {e}")

    def update_stats(self):
        """
        Переопределение метода обновления статистики для добавления истории и полосок.
        """
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')

            self.cpu_bar.setValue(int(cpu))
            self.ram_bar.setValue(int(ram.percent))

            self.stats_history.add_cpu(cpu)
            self.stats_history.add_ram(ram.percent)
            self.stats_history.add_disk(disk.free / (1024**3))

            cpu_avg = self.stats_history.get_cpu_avg()
            ram_avg = self.stats_history.get_ram_avg()

            self.history_label.setText(f"Avg CPU: {cpu_avg:.1f}% | Avg RAM: {ram_avg:.1f}%")
        except Exception as e:
            logging.error(f"Ошибка обновления истории: {e}")

    def apply_theme(self):
        """
        Переопределение применения темы для расширенных элементов.
        """
        super().apply_theme()
        font_family = self.config.get('font_family')

        bar_style = f"QProgressBar {{ border: 1px solid {self.theme_color}; border-radius: 2px; text-align: center; color: {self.theme_color}; background: transparent; }} QProgressBar::chunk {{ background-color: {self.theme_color}; }}"

        if hasattr(self, 'cpu_bar'):
            self.cpu_bar.setStyleSheet(bar_style)
        if hasattr(self, 'ram_bar'):
            self.ram_bar.setStyleSheet(bar_style)

        if hasattr(self, 'cpu_label'):
            self.cpu_label.setStyleSheet(f"color: {self.theme_color};")
        if hasattr(self, 'ram_label'):
            self.ram_label.setStyleSheet(f"color: {self.theme_color};")

        if hasattr(self, 'network_label'):
            self.network_label.setStyleSheet(f"color: {self.theme_color};")
            self.network_label.setFont(QFont(font_family, 9))

        if hasattr(self, 'temp_label'):
            self.temp_label.setStyleSheet(f"color: {self.theme_color};")
            self.temp_label.setFont(QFont(font_family, 9))

        if hasattr(self, 'history_label'):
            self.history_label.setStyleSheet(f"color: {self.theme_color};")
            self.history_label.setFont(QFont(font_family, 8))

    def contextMenuEvent(self, event):
        """
        Контекстное меню по правой кнопке.
        """
        menu = QMenu(self)

        pin_action = QAction("Закрепить/Открепить", self)
        pin_action.triggered.connect(self.toggle_pin)
        menu.addAction(pin_action)

        theme_menu = menu.addMenu("Сменить тему")

        cyan_action = QAction("Cyan", self)
        cyan_action.triggered.connect(lambda: self.change_theme('cyan'))
        theme_menu.addAction(cyan_action)

        red_action = QAction("Red", self)
        red_action.triggered.connect(lambda: self.change_theme('red'))
        theme_menu.addAction(red_action)

        green_action = QAction("Green", self)
        green_action.triggered.connect(lambda: self.change_theme('green'))
        theme_menu.addAction(green_action)

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)

        menu.exec_(event.globalPos())

    def toggle_pin(self):
        """
        Переключение закрепления поверх всех окон.
        """
        if self.windowFlags() & Qt.WindowStaysOnTopHint:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()

    def change_theme(self, theme):
        """
        Смена темы.
        """
        theme_colors = {
            'cyan': '#00ffcc',
            'red': '#ff0000',
            'green': '#00ff00'
        }
        if theme in theme_colors:
            self.theme_color = theme_colors[theme]
            try:
                self.apply_theme()
            except Exception as e:
                logging.error(f"Ошибка смены темы: {e}")

# Дополнительные утилитарные функции

def format_bytes(bytes_value):
    """
    Форматирование байтов в читаемый вид (KB, MB, GB).
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def get_system_info():
    """
    Получение общей информации о системе.
    """
    try:
        return {
            'os': os.name,
            'platform': sys.platform,
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total
        }
    except Exception as e:
        logging.error(f"Ошибка получения системной информации: {e}")
        return {}

def log_system_info():
    """
    Логирование системной информации при запуске.
    """
    info = get_system_info()
    logging.info(f"Системная информация: {info}")

def create_backup_notes():
    """
    Создание резервной копии заметок.
    """
    try:
        if os.path.exists("notes.txt"):
            backup_name = f"notes_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open("notes.txt", "r", encoding="utf-8") as src:
                with open(backup_name, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
            logging.info(f"Резервная копия заметок создана: {backup_name}")
    except Exception as e:
        logging.error(f"Ошибка создания резервной копии: {e}")

def cleanup_old_backups(max_backups=5):
    """
    Очистка старых резервных копий заметок.
    """
    try:
        backups = [f for f in os.listdir('.') if f.startswith('notes_backup_') and f.endswith('.txt')]
        backups.sort(reverse=True)
        if len(backups) > max_backups:
            for old_backup in backups[max_backups:]:
                os.remove(old_backup)
                logging.info(f"Удалена старая резервная копия: {old_backup}")
    except Exception as e:
        logging.error(f"Ошибка очистки резервных копий: {e}")

# Дополнительные константы и переменные

THEMES = {
    'cyberpunk': {
        'text_color': '#00ffcc',
        'background_alpha': 0.5
    },
    'minimalist': {
        'text_color': '#ffffff',
        'background_alpha': 0.3
    },
    'dark': {
        'text_color': '#ff6600',
        'background_alpha': 0.7
    }
}

DEFAULT_FONTS = ['Consolas', 'Segoe UI Semibold', 'Arial', 'Courier New']

UPDATE_INTERVALS = {
    'fast': {'clock': 500, 'stats': 1000, 'network': 2000, 'temp': 3000},
    'normal': {'clock': 1000, 'stats': 2000, 'network': 3000, 'temp': 5000},
    'slow': {'clock': 2000, 'stats': 5000, 'network': 5000, 'temp': 10000}
}

# Функции для обработки ошибок

def handle_exception(func):
    """
    Декоратор для обработки исключений в функциях.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Ошибка в функции {func.__name__}: {e}")
            return None
    return wrapper

# Применение декоратора к некоторым функциям
@handle_exception
def safe_load_config(config):
    return config.load_config()

@handle_exception
def safe_save_config(config):
    config.save_config()

@handle_exception
def safe_update_clock(widget):
    widget.update_clock()

@handle_exception
def safe_update_stats(widget):
    widget.update_stats()

# Дополнительные методы для класса Config

class ExtendedConfig(Config):
    """
    Расширенная версия конфигурации с дополнительными настройками.
    """
    def __init__(self):
        super().__init__()
        self.extended_defaults = {
            'show_network': True,
            'show_temperature': True,
            'show_history': True,
            'backup_notes': True,
            'max_backups': 5,
            'update_mode': 'normal'
        }
        self.default_config.update(self.extended_defaults)
        self.config = self.load_config()

    def get_update_intervals(self):
        """
        Получение интервалов обновления на основе режима.
        """
        mode = self.get('update_mode')
        return UPDATE_INTERVALS.get(mode, UPDATE_INTERVALS['normal'])

    def apply_theme_settings(self, theme_name):
        """
        Применение настроек темы.
        """
        if theme_name in THEMES:
            theme = THEMES[theme_name]
            self.set('text_color', theme['text_color'])
            self.set('background_alpha', theme['background_alpha'])

# Финальные дополнения и запуск

if __name__ == "__main__":
    log_system_info()  # Логирование системной информации
    create_backup_notes()  # Создание резервной копии заметок
    cleanup_old_backups()  # Очистка старых резервных копий

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Использование расширенного виджета
    widget = ExtendedSystemWidget()
    widget.show()

    # Обработка сигналов приложения
    def on_app_quit():
        logging.info("Приложение завершается")
        create_backup_notes()

    app.aboutToQuit.connect(on_app_quit)

    sys.exit(app.exec_())