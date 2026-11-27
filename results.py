import datetime

# Структура: user_id -> данные теста
user_results = {}

def start_test(user_id):
    """
    Инициализируем тест для пользователя
    """
    user_results[user_id] = {
        "start": datetime.datetime.now(),
        "correct": 0,
        "asked": 0
    }

def record_answer(user_id, correct_answer, chosen_answer):
    """
    Сохраняем ответ пользователя и возвращаем True/False
    """
    if user_id not in user_results:
        start_test(user_id)

    user_results[user_id]["asked"] += 1
    is_correct = correct_answer == chosen_answer
    if is_correct:
        user_results[user_id]["correct"] += 1

    return is_correct

def get_score(user_id):
    """
    Возвращает итоговые данные теста
    """
    if user_id not in user_results:
        return None

    data = user_results[user_id]
    end = datetime.datetime.now()
    duration = end - data["start"]
    percent = int(data["correct"] / data["asked"] * 100) if data["asked"] > 0 else 0

    return {
        "correct": data["correct"],
        "asked": data["asked"],
        "percent": percent,
        "start": data["start"],
        "end": end,
        "duration": duration
    }

def finish_test(user_id):
    """
    Удаляем данные пользователя после завершения
    """
    if user_id in user_results:
        del user_results[user_id]

