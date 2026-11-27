import random
import hashlib
from aiogram import types
from aiogram.types.input_file import FSInputFile
from data_loader import lines_data, areas_data, points_data, relief_data, water_data
from keyboards import create_test_keyboard
from messages import get_test_not_ready_text, get_question_prompt_text
from buttons import make_button

CATEGORY_MAP = {
    "lines1": lines_data,
    "areas1": areas_data,
    "points1": points_data,
    "relief1": relief_data,
    "water1": water_data
}

questions_store = {}  # qid -> dict с info о вопросе

async def handle_test(callback: types.CallbackQuery, test_type: str):
    data = CATEGORY_MAP.get(test_type)
    if not data:
        await callback.message.answer(get_test_not_ready_text())
        return

    concept, images = random.choice(list(data.items()))
    image_file = images[0]

    all_options = list(data.keys())
    all_options.remove(concept)
    wrong_options = random.sample(all_options, k=min(7, len(all_options)))
    options = wrong_options + [concept]
    random.shuffle(options)

    qid = hashlib.md5(concept.encode("utf-8")).hexdigest()[:8]

    answer_rows = [
        [make_button(opt, f"answer|{qid}|{i}")]
        for i, opt in enumerate(options)
    ]
    keyboard = create_test_keyboard(answer_rows)

    photo = FSInputFile(f"pictures/{image_file}")

    sent_message = await callback.message.answer_photo(
        photo=photo,
        caption=get_question_prompt_text(),
        reply_markup=keyboard
    )

    # Храним вопрос целиком: правильный ответ, варианты, тип теста, message_id
    questions_store[qid] = {
        "answer": concept,
        "options": options,
        "test_type": test_type,
        "message_id": sent_message.message_id,
        "chat_id": sent_message.chat.id
    }

