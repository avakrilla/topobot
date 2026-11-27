# TopoBot

Telegram-бот для тестирования знаний топографических знаков ГГЦ.

## Возможности

Бот предоставляет набор тестов по пяти тематическим направлениям:

- Линейные объекты
- Площадные объекты
- Точечные объекты
- Рельеф
- Водные объекты

Поддерживаются несколько вариантов тестирования, включая общий тест.

По результатам прохождения пользователь получает обратную связь по ответам и итоговую статистику.

## Технологии

- Python
- aiogram 3
- JSON

## Структура проекта

```text
topobot/
├── bot.py                # Основной файл бота
├── answer_helper.py      # Обработка ответов
├── buttons.py            # Кнопки
├── keyboards.py          # Клавиатуры
├── messages.py           # Тексты сообщений
├── data_loader.py        # Загрузка данных
├── results.py            # Учёт результатов
├── results_service.py    # Формирование итогов
├── tests_logic.py        # Логика тестов
├── tests_logic_2.py      # Логика тестов
├── tests_logic_3.py      # Общий тест
├── requirements.txt      # Зависимости
├── *.json                # Данные тестов
├── pictures/             # Изображения объектов
└── pictures_small/       # Уменьшенные изображения
```

## Установка

Клонировать репозиторий:

```bash
git clone git@github.com:avakrilla/topobot.git
cd topobot
```

Создать виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

## Настройка

Создать файл `.env` в корне проекта:

```env
BOT_TOKEN=your_telegram_bot_token
```

Получить токен бота можно через [@BotFather](https://t.me/BotFather).

## Запуск

```bash
python bot.py
```

## Запуск через systemd

Для постоянной работы бота можно использовать systemd.

Пример команды запуска:

```ini
ExecStart=/path/to/topobot/venv/bin/python3 /path/to/topobot/bot.py
```

## Репозиторий

[GitHub: avakrilla/topobot](https://github.com/avakrilla/topobot)

