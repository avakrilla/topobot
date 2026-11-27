import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from decouple import config
from answer_helper import AnswerContext, AnswerHelper
from keyboards import test_selection_keyboard, send_error_with_return, TEST_NAMES, create_processing_keyboard
from messages import (
    format_wrong_answer_feedback,
    get_correct_answer_feedback,
    format_user_answer_confirmation,
    get_processing_caption_text,
    get_processing_notice_text,
    get_question_not_found_text,
    get_select_test_prompt,
    get_start_message,
    get_test_cancelled_text,
    get_test_cancelled_alert,
    get_test_not_ready_text,
)
from results_service import send_final_result
from tests_logic import handle_test, questions_store
from tests_logic_2 import handle_test_2, handle_answer_2, questions_store_2
from tests_logic_3 import handle_general_test, handle_general_answer, general_questions_store
from results import record_answer, get_score, start_test, finish_test, user_results

BOT_TOKEN = config("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    """
    Стартовое меню бота с выбором теста
    """
    await message.answer(
        get_start_message(),
        reply_markup=test_selection_keyboard()
    )

@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    """
    Обработка всех нажатий кнопок
    """
    data = callback.data
    user_id = callback.from_user.id

    # --- Тест 1 ответы ---
    if data.startswith("answer|"):
        # Immediately answer callback to prevent duplicate clicks
        await callback.answer(get_processing_notice_text())
        
        _, qid, idx = data.split("|")
        idx = int(idx)

        if qid not in questions_store:
            await send_error_with_return(callback.message, get_question_not_found_text())
            return

        qdata = questions_store[qid]
        correct_answer = qdata["answer"]
        options = qdata["options"]
        test_type = qdata["test_type"]
        message_id = qdata.get("message_id")
        chat_id = qdata.get("chat_id", callback.message.chat.id)

        chosen_answer = options[idx]

        # Update keyboard and caption to show processing state
        processing_keyboard = create_processing_keyboard()
        try:
            if message_id:
                await bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=get_processing_caption_text(),
                    reply_markup=processing_keyboard
                )
        except Exception:
            pass  # Ignore errors if message was already edited or deleted

        if user_id not in user_results:  # первый вопрос
            start_test(user_id)

        is_correct = record_answer(user_id, correct_answer, chosen_answer)

        feedback_text = (
            get_correct_answer_feedback()
            if is_correct else
            format_wrong_answer_feedback(correct_answer)
        )

        context = AnswerContext(
            callback=callback,
            user_id=user_id,
            message_id=message_id,
            chat_id=chat_id,
        )

        del questions_store[qid]

        helper = AnswerHelper(
            context=context,
            confirm_text=format_user_answer_confirmation(chosen_answer),
            feedback_text=feedback_text,
            after_feedback=None,
            completion_check=lambda uid: user_results[uid]["asked"] >= 30,
            on_finish=lambda: finalize_test(callback, user_id, test_type),
            on_next_question=lambda: handle_test(callback, test_type),
        )
        await helper.process()

        return

    # --- Тест 2 ответы ---
    if data.startswith("answer2|"):
        await handle_answer_2(callback)
        return

    # --- Общий тест ответы (gans|qid|idx) ---
    if data.startswith("gans|"):
        await handle_general_answer(callback)
        return

    # --- Запуск общего теста ---
    if data == "general":
        await handle_general_test(callback)
        return

    # --- Кнопка "Пройти ещё тест" ---
    if data == "restart":
        await callback.message.answer(
            get_select_test_prompt(),
            reply_markup=test_selection_keyboard()
        )
        return

    # --- Кнопка "Главное меню" ---
    if data == "mainmenu":
        await callback.message.answer(
            get_select_test_prompt(),
            reply_markup=test_selection_keyboard()
        )
        return

    # --- Кнопка "Прервать тест" ---
    if data == "cancel_test":
        # Очищаем хранилище пользователя
        if user_id in user_results:
            del user_results[user_id]
        
        # Очищаем все вопросы из stores (они удаляются после ответа, но на всякий случай)
        questions_store.clear()
        questions_store_2.clear()
        general_questions_store.clear()
        
        await callback.message.answer(
            get_test_cancelled_text(),
            reply_markup=test_selection_keyboard()
        )
        await callback.answer(get_test_cancelled_alert())
        return

    # --- Запуск теста 1 или 2 ---
    if data in ["lines1", "areas1", "points1", "relief1", "water1"]:
        await handle_test(callback, data)
    elif data in ["lines2", "areas2", "points2", "relief2", "water2"]:
        await handle_test_2(callback, data)
    else:
        await callback.message.answer(get_test_not_ready_text())

async def finalize_test(callback: types.CallbackQuery, user_id: int, test_type: str):
    score = get_score(user_id)
    if not score:
        return

    username = callback.from_user.username or callback.from_user.full_name
    test_name = TEST_NAMES.get(test_type, test_type)
    await send_final_result(
        callback,
        score=score,
        username=username,
        test_name=test_name,
        layout_key="test1",
    )
    finish_test(user_id)

async def main():
    try:
        print("Бот запущен...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

