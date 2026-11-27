from aiogram import types

from messages import get_general_test_placeholder


async def handle_general_test(callback: types.CallbackQuery):
    await callback.message.answer(get_general_test_placeholder())

