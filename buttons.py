from aiogram.types import InlineKeyboardButton


def make_button(text: str, callback_data: str, **kwargs) -> InlineKeyboardButton:
    """
    Creates an InlineKeyboardButton from provided data.
    Useful for dynamically generated buttons.
    """
    return InlineKeyboardButton(text=text, callback_data=callback_data, **kwargs)


BUTTON_CONFIGS = {
    "restart_test": {
        "text": "Пройти ещё тест",
        "callback_data": "restart"
    },
    "main_menu": {
        "text": "Главное меню",
        "callback_data": "mainmenu"
    },
    "cancel_test": {
        "text": "Прервать тест",
        "callback_data": "cancel_test"
    },
}


def create_button(name: str, **overrides) -> InlineKeyboardButton:
    """
    Returns a ready-to-use InlineKeyboardButton by name.
    Additional keyword overrides (like callback_data) are allowed.
    """
    if name not in BUTTON_CONFIGS:
        raise ValueError(f"Unknown button name: {name}")

    config = {**BUTTON_CONFIGS[name], **overrides}
    return make_button(**config)


def get_restart_button(**overrides) -> InlineKeyboardButton:
    return create_button("restart_test", **overrides)


def get_main_menu_button(**overrides) -> InlineKeyboardButton:
    return create_button("main_menu", **overrides)


def get_cancel_test_button(**overrides) -> InlineKeyboardButton:
    return create_button("cancel_test", **overrides)

