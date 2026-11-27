import random
import hashlib
from aiogram import types
from aiogram.types import InputMediaPhoto, FSInputFile
from data_loader import lines_data, areas_data, points_data, relief_data, water_data
from results import record_answer, get_score, start_test, finish_test, user_results
from keyboards import create_test_keyboard, send_error_with_return, TEST_NAMES, create_processing_keyboard
from buttons import make_button
from answer_helper import AnswerContext, AnswerHelper
from results_service import send_final_result
from messages import (
    format_wrong_answer_feedback,
    get_correct_answer_feedback,
    format_user_answer_confirmation,
    get_correct_image_caption,
    get_image_send_error_text,
    get_image_choice_prompt,
    get_image_selection_intro,
    get_processing_caption_text,
    get_processing_notice_text,
    get_question_not_found_text,
    get_test_not_ready_text,
)

CATEGORY_MAP_2 = {
    "lines2": lines_data,
    "areas2": areas_data,
    "points2": points_data,
    "relief2": relief_data,
    "water2": water_data
}

questions_store_2 = {}  # qid -> dict с info о вопросе

async def handle_test_2(callback: types.CallbackQuery, test_type: str):
    data = CATEGORY_MAP_2.get(test_type)
    if not data:
        await callback.message.answer(get_test_not_ready_text())
        return

    concept, images = random.choice(list(data.items()))
    correct_image = images[0]

    # 3 случайные картинки других понятий
    all_concepts = list(data.keys())
    all_concepts.remove(concept)
    wrong_concepts = random.sample(all_concepts, k=min(3, len(all_concepts)))
    wrong_images = [data[c][0] for c in wrong_concepts]

    options = wrong_images + [correct_image]
    random.shuffle(options)

    qid = hashlib.md5(concept.encode("utf-8")).hexdigest()[:8]

    await callback.message.answer(get_image_selection_intro(concept))

    # Отправляем все 4 картинки разом как медиагруппу
    media = [InputMediaPhoto(media=FSInputFile(f"pictures_small/{img}")) for img in options]
    await callback.message.answer_media_group(media=media)

    # Клавиатура с кнопками 1 2 3 4 в один ряд
    answer_rows = [
        [make_button(str(i+1), f"answer2|{qid}|{i}") for i in range(4)]
    ]
    keyboard = create_test_keyboard(answer_rows)
    sent_message = await callback.message.answer(
        get_image_choice_prompt(),
        reply_markup=keyboard
    )

    questions_store_2[qid] = {
        "answer": correct_image,
        "options": options,
        "concept": concept,
        "test_type": test_type,
        "message_id": sent_message.message_id,
        "chat_id": sent_message.chat.id
    }


async def handle_answer_2(callback: types.CallbackQuery):
    """
    Обработка ответов теста 2
    """
    # Immediately answer callback to prevent duplicate clicks
    await callback.answer(get_processing_notice_text())
    
    data = callback.data
    _, qid, idx = data.split("|")
    idx = int(idx)
    user_id = callback.from_user.id

    if qid not in questions_store_2:
        await send_error_with_return(callback.message, get_question_not_found_text())
        return

    qdata = questions_store_2[qid]
    correct_image = qdata["answer"]
    options = qdata["options"]
    test_type = qdata["test_type"]
    message_id = qdata.get("message_id")
    chat_id = qdata.get("chat_id", callback.message.chat.id)

    chosen_image = options[idx]

    # Update keyboard and text to show processing state
    processing_keyboard = create_processing_keyboard()
    try:
        if message_id:
            await callback.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=get_processing_caption_text(),
                reply_markup=processing_keyboard
            )
    except Exception:
        pass  # Ignore errors if message was already edited or deleted

    if user_id not in user_results:
        start_test(user_id)

    is_correct = record_answer(user_id, correct_image, chosen_image)

    if is_correct:
        feedback_text = get_correct_answer_feedback()
    else:
        correct_number = options.index(correct_image) + 1
        feedback_text = format_wrong_answer_feedback(str(correct_number))

    async def after_feedback():
        if not is_correct:
            try:
                await callback.message.answer_photo(
                    photo=FSInputFile(f"pictures_small/{correct_image}"),
                    caption=get_correct_image_caption()
                )
            except Exception:
                await callback.message.answer(get_image_send_error_text())

    context = AnswerContext(
        callback=callback,
        user_id=user_id,
        message_id=message_id,
        chat_id=chat_id,
    )

    del questions_store_2[qid]

    helper = AnswerHelper(
        context=context,
        confirm_text=format_user_answer_confirmation(str(idx + 1)),
        feedback_text=feedback_text,
        after_feedback=after_feedback,
        completion_check=lambda uid: user_results[uid]["asked"] >= 30,
        on_finish=lambda: finalize_test_2(callback, user_id, test_type),
        on_next_question=lambda: handle_test_2(callback, test_type),
    )
    await helper.process()


async def finalize_test_2(callback: types.CallbackQuery, user_id: int, test_type: str):
    score = get_score(user_id)
    if not score:
        return

    username = callback.from_user.username or callback.from_user.full_name
    percent = score["percent"]
    start_time = score["start"].strftime("%d.%m.%Y %H:%M:%S")
    end_time = score["end"].strftime("%d.%m.%Y %H:%M:%S")
    duration = str(score["duration"]).split(".")[0]

    test_name = TEST_NAMES.get(test_type, test_type)

    await send_final_result(
        callback,
        score=score,
        username=username,
        test_name=test_name,
        layout_key="default",
    )
    finish_test(user_id)

