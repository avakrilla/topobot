# tests_logic_3.py
import random
import hashlib
import asyncio
from pathlib import Path
from aiogram import types
from aiogram.types.input_file import FSInputFile
from aiogram.exceptions import TelegramNetworkError
from data_loader import all_data  # all.json загружается как all_data
from results import start_test, record_answer, get_score, finish_test, user_results
from keyboards import create_test_keyboard, send_error_with_return, TEST_NAMES, create_processing_keyboard
from buttons import get_main_menu_button, get_restart_button, make_button
from answer_helper import AnswerContext, AnswerHelper
from results_service import send_final_result
from messages import (
    format_basic_result,
    format_wrong_answer_feedback,
    get_correct_answer_feedback,
    format_user_answer_confirmation,
    get_file_missing_warning,
    get_general_caption_text,
    get_general_data_missing_text,
    get_image_delivery_error_text,
    get_invalid_format_text,
    get_invalid_option_text,
    get_processing_caption_text,
    get_processing_notice_text,
    get_question_not_found_text,
    get_question_not_found_or_expired_text,
)

BASE_DIR = Path(__file__).parent
PICTURES_DIR = BASE_DIR / "pictures"  # ты сказал: брать из pictures/

# store: qid -> { "answer": correct_concept, "options": [...names...], "test_type": "general" }
general_questions_store = {}

# Утилита безопасной отправки с ретраями на сетевые ошибки
async def safe_send(func, *args, retries=3, backoff=1, **kwargs):
    last_exc = None
    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except TelegramNetworkError as e:
            last_exc = e
            # короткий экспоненциальный бэк-офф
            await asyncio.sleep(backoff * (2 ** attempt))
    # если все попытки не прошли — пробросим последнюю ошибку
    raise last_exc

async def handle_general_test(callback: types.CallbackQuery):
    """
    Запуск/продолжение общего теста: формирует и отправляет один вопрос.
    Формат ответа (callback_data) — "gans|<qid>|<index>"
    """
    # Берём 100 вопросов по вызовам handle_general_test — но здесь отправляем по одному вопросу.
    # Генерируем 1 случайный вопрос (допускаем повторы).
    # Выбираем случайный объект из all_data (ключ = понятие, value = список файлов)
    if not all_data:
        await safe_send(callback.message.answer, get_general_data_missing_text())
        return

    # выбрать понятие
    concept = random.choice(list(all_data.keys()))
    images = all_data[concept]
    # выбираем одну картинку из списка, если несколько
    image_file = random.choice(images)

    # формируем 8 вариантов текста (названий): правильный + 7 случайных
    all_concepts = list(all_data.keys())
    # Убрать правильный для подбора неправильных
    other_concepts = [c for c in all_concepts if c != concept]
    # если всего <7 неправильных, берем сколько есть (потом будут повторы)
    wrong_count = min(7, len(other_concepts))
    wrong_options = random.sample(other_concepts, k=wrong_count) if wrong_count > 0 else []
    # если нужно добрать до 7 (малые наборы) — добавляем случайные повторы
    while len(wrong_options) < 7:
        wrong_options.append(random.choice(other_concepts) if other_concepts else concept)

    options = wrong_options + [concept]
    random.shuffle(options)

    # короткий qid
    qid = hashlib.md5((concept + str(random.random())).encode("utf-8")).hexdigest()[:8]

    # Проверяем существование файла
    image_path = PICTURES_DIR / image_file
    if not image_path.exists():
        # если файл отсутствует, логичнее пропустить этот вопрос и вызвать следующий
        await safe_send(
            callback.message.answer,
            get_file_missing_warning(image_file),
            parse_mode="Markdown"
        )
        # рекурсивно вызываем следующий
        await handle_general_test(callback)
        return

    photo = FSInputFile(str(image_path))

    # Клавиатура: 8 кнопок, каждая в своей строке
    answer_rows = []
    for idx, option_text in enumerate(options):
        answer_rows.append([
            make_button(option_text, f"gans|{qid}|{idx}")
        ])
    
    keyboard = create_test_keyboard(answer_rows)

    # Отправляем фото и клавиатуру
    caption = get_general_caption_text()
    try:
        sent_message = await safe_send(
            callback.message.answer_photo,
            photo=photo,
            caption=caption,
            reply_markup=keyboard
        )
        
        general_questions_store[qid] = {
            "answer": concept,
            "options": options,
            "image": image_file,
            "test_type": "general",
            "message_id": sent_message.message_id,
            "chat_id": sent_message.chat.id
        }
    except Exception as e:
        # Если вообще не удалось отправить изображение, пробуем следующий
        await safe_send(callback.message.answer, get_image_delivery_error_text(e))
        return

async def handle_general_answer(callback: types.CallbackQuery):
    """
    Обработка ответов общего теста — ожидаем callback_data формата "gans|<qid>|<index>"
    """
    # Immediately answer callback to prevent duplicate clicks
    await callback.answer(get_processing_notice_text())
    
    data = callback.data
    try:
        _, qid, idx = data.split("|")
        idx = int(idx)
    except Exception:
        await send_error_with_return(callback.message, get_invalid_format_text(), send_func=safe_send)
        return

    if qid not in general_questions_store:
        await send_error_with_return(
            callback.message,
            get_question_not_found_or_expired_text(),
            send_func=safe_send
        )
        return

    q = general_questions_store[qid]
    options = q["options"]
    correct = q["answer"]
    message_id = q.get("message_id")
    chat_id = q.get("chat_id", callback.message.chat.id)
    
    # guard index
    if idx < 0 or idx >= len(options):
        await send_error_with_return(
            callback.message,
            get_invalid_option_text(),
            send_func=safe_send
        )
        return

    chosen = options[idx]
    user_id = callback.from_user.id

    # Update keyboard and caption to show processing state
    processing_keyboard = create_processing_keyboard()
    try:
        if message_id:
            await callback.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=get_processing_caption_text(),
                reply_markup=processing_keyboard
            )
    except Exception:
        pass  # Ignore errors if message was already edited or deleted

    # стартуем тест для пользователя при первом ответе
    if user_id not in user_results:
        start_test(user_id)

    is_correct = record_answer(user_id, correct, chosen)
    feedback_text = (
        get_correct_answer_feedback()
        if is_correct else
        format_wrong_answer_feedback(correct)
    )

    context = AnswerContext(
        callback=callback,
        user_id=user_id,
        message_id=message_id,
        chat_id=chat_id,
        send_func=safe_send,
    )

    del general_questions_store[qid]

    helper = AnswerHelper(
        context=context,
        confirm_text=format_user_answer_confirmation(chosen),
        feedback_text=feedback_text,
        after_feedback=None,
        completion_check=lambda uid: user_results[uid]["asked"] >= 100,
        on_finish=lambda: finalize_general_test(callback, user_id),
        on_next_question=lambda: handle_general_test(callback),
    )
    await helper.process()


async def finalize_general_test(callback: types.CallbackQuery, user_id: int):
    score = get_score(user_id)
    if not score:
        return

    username = callback.from_user.username or callback.from_user.full_name
    percent = score["percent"]
    start_time = score["start"].strftime("%d.%m.%Y %H:%M:%S")
    end_time = score["end"].strftime("%d.%м.%Y %H:%M:%S")
    duration = str(score["duration"]).split(".")[0]

    test_name = TEST_NAMES.get("general", "Общие")
    await send_final_result(
        callback,
        score=score,
        username=username,
        test_name=test_name,
        layout_key="general",
        send_func=safe_send,
    )
    finish_test(user_id)

