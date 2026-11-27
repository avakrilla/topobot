from aiogram import types
from aiogram.types import InlineKeyboardMarkup

from buttons import get_cancel_test_button, make_button
from messages import get_select_test_prompt

# Array of test objects with text and value
TESTS = [
    {"text": "Линейные1", "value": "lines1"},
    {"text": "Линейные2", "value": "lines2"},
    {"text": "Площадные1", "value": "areas1"},
    {"text": "Площадные2", "value": "areas2"},
    {"text": "Точечные1", "value": "points1"},
    {"text": "Точечные2", "value": "points2"},
    {"text": "Водные1", "value": "water1"},
    {"text": "Водные2", "value": "water2"},
    {"text": "Рельеф1", "value": "relief1"},
    {"text": "Рельеф2", "value": "relief2"},
    {"text": "Общие", "value": "general"}
]

# Helper dictionary for quick access by value
TEST_NAMES = {test["value"]: test["text"] for test in TESTS}

def test_selection_keyboard():
    buttons = []
    # Create buttons in pairs (2 per row), except the last one
    for i in range(0, len(TESTS) - 1, 2):
        row = [
            make_button(TESTS[i]["text"], TESTS[i]["value"]),
            make_button(TESTS[i + 1]["text"], TESTS[i + 1]["value"])
        ]
        buttons.append(row)
    
    # Add the last button (general) as a single button row
    if len(TESTS) % 2 == 1:
        buttons.append([
            make_button(TESTS[-1]["text"], TESTS[-1]["value"])
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def create_test_keyboard(answer_rows):
    """
    Creates a keyboard with answer buttons and cancel button
    Args:
        answer_rows: list of rows, each row is a list of InlineKeyboardButton objects
    Returns:
        InlineKeyboardMarkup with answer buttons and cancel button
    """
    cancel_row = [get_cancel_test_button()]
    keyboard_rows = answer_rows + [cancel_row]
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

def create_processing_keyboard():
    """
    Creates a keyboard with only "Cancel test" button for processing state
    Returns:
        InlineKeyboardMarkup with cancel button only
    """
    cancel_row = [get_cancel_test_button()]
    return InlineKeyboardMarkup(inline_keyboard=[cancel_row])

async def send_error_with_return(message: types.Message, error_text: str, send_func=None):
    """
    Sends error message and then shows test selection menu
    Args:
        message: Message object to send error to
        error_text: Text of the error message
        send_func: Optional function to use for sending (e.g., safe_send), if None uses message.answer
    """
    keyboard = test_selection_keyboard()
    prompt = get_select_test_prompt()
    if send_func:
        await send_func(message.answer, error_text)
        await send_func(message.answer, prompt, reply_markup=keyboard)
    else:
        await message.answer(error_text)
        await message.answer(prompt, reply_markup=keyboard)

