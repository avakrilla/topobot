from __future__ import annotations

START_MESSAGE = "Привет! Я бот теста на знание топознаков. Выбери тест для прохождения:"
SELECT_TEST_PROMPT = "Выбери тест для прохождения:"
TEST_NOT_READY_TEXT = "Тест пока не готов."
TEST_CANCELLED_TEXT = "Тест прерван. Выбери тест для прохождения:"
TEST_CANCELLED_ALERT = "Тест прерван"
IMAGE_CHOICE_PROMPT_TEXT = "Выбери правильную картинку кнопкой ниже:"
QUESTION_PROMPT_TEXT = "Выбери правильный ответ:"
GENERAL_CAPTION_TEXT = "Вопрос (общий). Картинка — выбери правильный вариант (1–8):"
GENERAL_DATA_MISSING_TEXT = "Данные для общего теста не найдены."
PROCESSING_NOTICE_TEXT = "⏳ Обработка..."
PROCESSING_CAPTION_TEXT = "⏳ Обработка ответа..."
QUESTION_NOT_FOUND_TEXT = "Ошибка: вопрос не найден."
QUESTION_NOT_FOUND_OR_EXPIRED_TEXT = "Ошибка: вопрос не найден или устарел."
INVALID_FORMAT_TEXT = "Неверный формат ответа."
INVALID_OPTION_TEXT = "Некорректный номер варианта."
CORRECT_IMAGE_CAPTION = "Правильная картинка"
IMAGE_SEND_ERROR_TEXT = "Не удалось показать правильную картинку."


def get_start_message() -> str:
    return START_MESSAGE


def get_select_test_prompt() -> str:
    return SELECT_TEST_PROMPT


def get_test_not_ready_text() -> str:
    return TEST_NOT_READY_TEXT


def get_test_cancelled_text() -> str:
    return TEST_CANCELLED_TEXT


def get_test_cancelled_alert() -> str:
    return TEST_CANCELLED_ALERT


def get_correct_answer_feedback() -> str:
    return "✅ Правильно!"


def format_wrong_answer_feedback(correct_value: str) -> str:
    return f"❌ Неправильно! Правильный ответ: {correct_value}"


def format_user_answer_confirmation(answer_value: str) -> str:
    return f"Ваш ответ: {answer_value}"


def _color_comment(percent: int) -> tuple[str, str]:
    if percent < 30:
        return "🟪", "Попробуйте ещё раз."
    if percent < 70:
        return "🟥", "Нужно ещё поучить."
    if percent < 90:
        return "🟨", "Молодец, осталось немного!"
    if percent < 100:
        return "🟩", "Отлично, почти 100%!"
    return "🟦✨", "Идеально! 100%, супер!"


def format_test1_result(
    percent: int,
    username: str,
    start_time: str,
    end_time: str,
    duration: str,
    test_name: str,
) -> str:
    color, comment = _color_comment(percent)
    return (
        f"{color} Тест {test_name} завершён.\n"
        f"Пользователь @{username}\n"
        f"Результат: {percent}%\n"
        f"Начало: {start_time}\n"
        f"Окончание: {end_time}\n"
        f"Время прохождения: {duration}\n\n"
        f"{comment}"
    )


def _basic_comment(percent: int) -> str:
    if percent == 100:
        return "Отлично! Готово на все 100%, продолжай в том же духе!"
    if percent >= 80:
        return "Молодец, осталось немного!"
    if percent >= 50:
        return "Неплохо, но нужно еще поучить."
    return "Попробуй еще раз."


def format_basic_result(
    percent: int,
    username: str,
    start_time: str,
    end_time: str,
    duration: str,
    test_name: str,
) -> str:
    comment = _basic_comment(percent)
    return (
        f"📊 Пользователь @{username} прошел тест {test_name} на {percent}%\n"
        f"Начало теста: {start_time}\n"
        f"Окончание теста: {end_time}\n"
        f"Время прохождения теста: {duration}\n"
        f"{comment}"
    )


def get_image_selection_intro(concept: str) -> str:
    return f"Выбери правильную картинку для понятия: {concept}"


def get_image_choice_prompt() -> str:
    return IMAGE_CHOICE_PROMPT_TEXT


def get_question_prompt_text() -> str:
    return QUESTION_PROMPT_TEXT


def get_general_caption_text() -> str:
    return GENERAL_CAPTION_TEXT

def get_general_data_missing_text() -> str:
    return GENERAL_DATA_MISSING_TEXT


def get_file_missing_warning(image_file: str) -> str:
    text = f"Файл изображения отсутствует: `{image_file}` — пропускаю вопрос."
    return text


def get_image_delivery_error_text(error: Exception | str) -> str:
    return f"Не удалось отправить изображение: {error}"


def get_general_test_placeholder() -> str:
    return "Это общий тест. Вопросы будут скоро."


def get_correct_image_caption() -> str:
    return CORRECT_IMAGE_CAPTION


def get_image_send_error_text() -> str:
    return IMAGE_SEND_ERROR_TEXT

def get_processing_notice_text() -> str:
    return PROCESSING_NOTICE_TEXT


def get_processing_caption_text() -> str:
    return PROCESSING_CAPTION_TEXT


def get_question_not_found_text() -> str:
    return QUESTION_NOT_FOUND_TEXT


def get_question_not_found_or_expired_text() -> str:
    return QUESTION_NOT_FOUND_OR_EXPIRED_TEXT


def get_invalid_format_text() -> str:
    return INVALID_FORMAT_TEXT


def get_invalid_option_text() -> str:
    return INVALID_OPTION_TEXT

