import json

from src.utils import (get_a_curse, get_data_time, get_path_and_period, get_the_stock_price, take_the_card_number,
                       timed_message, top_transactions)


def greetings_on_time(data_time: str) -> str:  # неизвестный тип данных значений ключа
    """Функция принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS,
    Возвращает Json ответ"""
    # Приветствие
    greetings = timed_message()

    time_period = get_data_time(data_time)

    sorted_df = get_path_and_period("../data/operations.xlsx", time_period)

    # Каждая карта
    cards = take_the_card_number(sorted_df)

    # Топ 5 транзакций по сумме
    top_transactions_5 = top_transactions(sorted_df, 5)

    # Курс валют
    curse = get_a_curse("../data/user_settings.json")

    # Стоимость акций
    stock_data = get_the_stock_price("../data/user_settings.json")

    data = {
        "greeting": greetings,
        "cards": cards,
        "top_transactions": top_transactions_5,
        "currency_rates": curse,
        "stock_prices": stock_data,
    }
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return json_data