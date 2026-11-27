from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence

from aiogram import types
from aiogram.types import InlineKeyboardMarkup

from buttons import get_restart_button, get_main_menu_button
from messages import format_basic_result, format_test1_result


Formatter = Callable[[Dict], str]


@dataclass
class ResultLayout:
    formatter: Formatter
    buttons: Sequence[str]


BUTTON_FACTORIES = {
    "restart": get_restart_button,
    "mainmenu": get_main_menu_button,
}

RESULT_LAYOUTS = {
    "test1": ResultLayout(formatter=format_test1_result, buttons=["restart"]),
    "default": ResultLayout(formatter=format_basic_result, buttons=["restart"]),
    "general": ResultLayout(formatter=format_basic_result, buttons=["restart", "mainmenu"]),
}


def build_keyboard(button_names: Sequence[str]) -> InlineKeyboardMarkup:
    rows: List[List[types.InlineKeyboardButton]] = [
        [BUTTON_FACTORIES[name]()]
        for name in button_names
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def send_result(
    callback: types.CallbackQuery,
    *,
    layout: ResultLayout,
    formatter_args: Dict,
):
    text = layout.formatter(**formatter_args)
    keyboard = build_keyboard(layout.buttons)
    await callback.message.answer(text, reply_markup=keyboard)


async def send_final_result(
    callback: types.CallbackQuery,
    *,
    score: Dict,
    username: str,
    test_name: str,
    layout_key: str,
    send_func: Callable[..., Awaitable] | None = None,
):
    layout = RESULT_LAYOUTS[layout_key]
    formatter_args = {
        "percent": score["percent"],
        "username": username,
        "start_time": score["start"].strftime("%d.%m.%Y %H:%M:%S"),
        "end_time": score["end"].strftime("%d.%m.%Y %H:%M:%S"),
        "duration": str(score["duration"]).split(".")[0],
        "test_name": test_name,
    }
    if send_func:
        text = layout.formatter(**formatter_args)
        keyboard = build_keyboard(layout.buttons)
        await send_func(callback.message.answer, text, reply_markup=keyboard)
    else:
        await send_result(
            callback,
            layout=layout,
            formatter_args=formatter_args,
        )

