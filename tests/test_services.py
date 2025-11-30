import pandas as pd

from src.services import cashback_analysis


def test_function_returns_json() -> None:
    """Тест возвращает JSON строку"""
    # Создаем тестовые данные
    test_data = {
        "Дата операции": ["01.03.2018 10:00:00"],
        "Кэшбэк": [5],
        "Сумма платежа": [-2000],
        "Категория": ["Магазин"],
    }

    df = pd.DataFrame(test_data)

    # Сохраняем в файл
    df.to_excel("test_file.xlsx", index=False)

    # Вызываем функцию
    result = cashback_analysis("test_file.xlsx", 2018, 3)

    # Проверяем результат
    assert isinstance(result, str)
    assert "Магазин" in result


def test_no_data_returns_empty_json() -> None:
    """Тест пустой JSON"""
    test_data = {
        "Дата операции": ["01.01.2020 10:00:00"],
        "Кэшбэк": [0],
        "Сумма платежа": [100],
        "Категория": ["Тест"],
    }

    df = pd.DataFrame(test_data)
    df.to_excel("test_file.xlsx", index=False)

    result = cashback_analysis("test_file.xlsx", 2018, 3)

    assert result == "{}"
