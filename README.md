# System Widget for Windows 11

A lightweight desktop system widget designed for professional developers and streamers. Features a cyberpunk/minimalist theme with transparent background, digital clock, pinned notes, and real-time system statistics.

## Features

- **Transparent Background**: No window borders, always on top
- **Draggable Interface**: Click and drag anywhere to move the widget
- **Digital Clock**: Large HH:MM:SS display
- **Pinned Notes**: Auto-saving text area for reminders (saved to notes.txt)
- **System Stats**: Real-time CPU, RAM, and Disk C: space monitoring
- **Cyberpunk Theme**: Neon cyan colors with minimalist design

## Requirements

- Windows 11
- Python 3.8+
- PyQt5
- psutil

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Building and Testing

- To build the package: `pip install -e .`
- To run tests: `python -m pytest test_main.py`
- CI/CD is handled via GitHub Actions (see `.github/workflows/ci.yml`)

## Usage

- The widget appears on screen and stays on top
- Drag it by clicking and holding anywhere on the widget
- Type notes in the text area - they save automatically
- Close by terminating the process (Ctrl+C in terminal)

## Code Quality

- Optimized for low CPU usage (<1%)
- Comments in Russian for code explanation
- Modular structure with PyQt5 and psutil integration

---

# Системний віджет для Windows 11

Легкий десктопний системний віджет, розроблений для професійних розробників та стримерів. Має кіберпанковий/мінімалістичний дизайн з прозорим фоном, цифровий годинник, прикріплені нотатки та статистику системи в реальному часі.

## Особливості

- **Прозорий фон**: Без рамок вікна, завжди зверху
- **Перетягуваний інтерфейс**: Клацніть і перетягніть де завгодно, щоб перемістити віджет
- **Цифровий годинник**: Великий дисплей HH:MM:SS
- **Прикріплені нотатки**: Автозберігаюча текстова область для нагадувань (збережено в notes.txt)
- **Статистика системи**: Моніторинг CPU, RAM та місця на диску C: в реальному часі
- **Кіберпанкова тема**: Неонові кольори ціану з мінімалістичним дизайном

## Вимоги

- Windows 11
- Python 3.8+
- PyQt5
- psutil

## Встановлення

1. Клонувати репозиторій
2. Встановити залежності: `pip install -r requirements.txt`
3. Запустити: `python main.py`

## Використання

- Віджет з'являється на екрані та залишається зверху
- Перетягніть його, клацнувши та утримуючи де завгодно на віджеті
- Введіть нотатки в текстову область - вони зберігаються автоматично
- Закрийте, завершивши процес (Ctrl+C в терміналі)

## Якість коду

- Оптимізовано для низького використання CPU (<1%)
- Коментарі російською мовою для пояснення коду
- Модульна структура з інтеграцією PyQt5 та psutil