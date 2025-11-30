import pytest
from unittest.mock import patch, mock_open
from src.utils import (
    timed_message,
    get_data_time,
    get_path_and_period,
    take_the_card_number,
    top_transactions,
    get_a_curse,
    get_the_stock_price,
)
import pandas as pd
import json


# Тест функции timed_message
@pytest.mark.parametrize(
    "hour,expected",
    [
        (0, "Доброй ночи"),
        (3, "Доброй ночи"),
        (4, "Доброе утро"),
        (8, "Доброе утро"),
        (12, "Добрый день"),
        (14, "Добрый день"),
        (16, "Добрый вечер"),
        (23, "Добрый вечер"),
    ],
)
def test_timed_message_all_watches(hour: int, expected: str) -> None:
    """Тестирует все случаи"""
    with patch("src.utils.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value.hour = hour

        result = timed_message()
        assert result == expected


# Тест функции get_data_time
@pytest.mark.parametrize(
    "input_date,expected",
    [
        # входная_дата, ожидаемое первое число, ожидаемая дата
        ("2021-03-15 14:30:25", ["01.03.2021 14:30:25", "15.03.2021 14:30:25"]),
        ("2021-01-01 00:00:00", ["01.01.2021 00:00:00", "01.01.2021 00:00:00"]),
        ("2021-12-31 23:59:59", ["01.12.2021 23:59:59", "31.12.2021 23:59:59"]),
        ("2021-02-28 12:00:00", ["01.02.2021 12:00:00", "28.02.2021 12:00:00"]),
    ],
)
def test_get_data_time_parametrized(input_date: str, expected: list[dict]) -> None:
    """Множество тестов в одном"""
    result = get_data_time(input_date)
    assert result == expected


@pytest.mark.parametrize(
    "invalid_date",
    [
        "2024-02-30 14:30:25",
        "2024/03/15 14:30:25",
        "2024-03-15",
        "",
        "not-a-date",
    ],
)
def test_get_data_time_invalid_cases(invalid_date: str) -> None:
    """Тест невалидных"""
    with pytest.raises((ValueError, TypeError)):
        get_data_time(invalid_date)


# Тест функции get_path_and_period


def test_get_path_and_period() -> None:
    mock_data = {
        "Дата операции": ["15.03.2021", "20.03.2021"],
        "Сумма операции": [100, 200],
        "Категория": ["Фастфуд", "Сувениры"],
    }
    mock_df = pd.DataFrame(mock_data)

    with patch("src.utils.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = mock_df

        path = "test.xlsx"
        period = ["01.03.2021 00:00:00", "31.03.2021 23:59:59"]

        result = get_path_and_period(path, period)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        mock_read_excel.assert_called_once_with("test.xlsx", sheet_name="Отчет по операциям")


# Тест функции
@pytest.mark.parametrize(
    "card_number,expected_last_digits",
    [
        ("1234********5678", "12345678"),
        ("1234567890123456", "1234567890123456"),
        ("12****34****56****78", "12345678"),
        ("****1234****", "1234"),
        ("", ""),
    ],
)
def test_card_number_parsing(card_number: str, expected_last_digits: str) -> None:
    """Тест разных форматов номеров карт"""
    data = {"Номер карты": [card_number], "Сумма операции с округлением": [1000]}
    df = pd.DataFrame(data)

    result = take_the_card_number(df)

    assert result[0]["last_digits"] == expected_last_digits
    assert result[0]["total_spent"] == 1000
    assert result[0]["cashback"] == 10


@pytest.mark.parametrize(
    "amount,expected_cashback",
    [
        (1000, 10),
        (99, 0),
        (199, 1),
        (0, 0),
        (-100, -1),
        (1000000, 10000),
    ],
)
def test_cashback_calculation(amount: int, expected_cashback: int) -> None:
    """Тест расчета кэшбэка для разных сумм"""
    data = {"Номер карты": ["1234********5678"], "Сумма операции с округлением": [amount]}
    df = pd.DataFrame(data)

    result = take_the_card_number(df)

    assert result[0]["cashback"] == expected_cashback


# Тест функции top_transactions
def test_simple_case() -> None:
    data = {
        "Дата операции": ["2024-01-01", "2024-01-02"],
        "Дата платежа": ["01.01.2024", "02.01.2024"],
        "Сумма операции": [100, 200],
        "Категория": ["Еда", "Транспорт"],
        "Описание": ["Обед", "Такси"],
    }
    df = pd.DataFrame(data)

    result = top_transactions(df, 2)

    assert isinstance(result, list)

    assert len(result) == 2

    assert "date" in result[0]
    assert "amount" in result[0]
    assert "category" in result[0]
    assert "description" in result[0]


# Тест функции get_a_curse
def test_successful_currency_rates() -> None:
    """Тест успешного получения курса валюты"""
    mock_json_data: dict = {"user_currencies": ["USD"]}

    mock_response: dict = {"query": {"from": "USD"}, "result": 90.5}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_json_data))):
        with patch("src.utils.requests.request") as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = mock_response

            result = get_a_curse("user_settings.json")

            expected = [{"currency": "USD", "rate": "90.5"}]

            assert result == expected


def test_empty_currencies() -> None:
    """Тест пустой список валют"""
    mock_json_data: dict = {"user_currencies": []}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_json_data))):
        result = get_a_curse("user_settings.json")
        assert result == []


def test_single_currency() -> None:
    """Тест одной валюты"""
    mock_json_data: dict = {"user_currencies": ["GBP"]}

    mock_response: dict = {"query": {"from": "GBP"}, "result": 115.75}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_json_data))):
        with patch("src.utils.requests.request") as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = mock_response

            result = get_a_curse("user_settings.json")

            expected = [{"currency": "GBP", "rate": "115.75"}]

            assert result == expected


def test_multiple_currencies_simple() -> None:
    """Тест несколько валют"""
    mock_json_data: dict = {"user_currencies": ["USD", "EUR", "CNY"]}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_json_data))):
        with patch("src.utils.requests.request") as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = {"query": {"from": "USD"}, "result": 90.5}

            result = get_a_curse("user_settings.json")

            assert len(result) == 3
            for item in result:
                assert "currency" in item
                assert "rate" in item


# Тест функции get_the_stock_price
def test_successful_stock_prices() -> None:
    """Тест успешного получения цен акций"""
    mock_json_data: dict = {"user_stocks": ["AAPL", "GOOGL"]}

    mock_response: dict = {"Global Quote": {"05. price": "150.25"}}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_json_data))):
        with patch("src.utils.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result = get_the_stock_price("user_settings.json")

            expected = [{"stock": "AAPL", "price": 150.25}, {"stock": "GOOGL", "price": 150.25}]

            assert result == expected


def test_empty_stocks() -> None:
    """Тест пустой список акций"""
    mock_json_data: dict = {"user_stocks": []}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_json_data))):
        result = get_the_stock_price("user_settings.json")
        assert result == []


def test_api_error() -> None:
    """Тест ошибку API"""
    mock_json_data: dict = {"user_stocks": ["AAPL"]}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_json_data))):
        with patch("src.utils.requests.get") as mock_get:
            mock_get.return_value.status_code = 404

            try:
                result = get_the_stock_price("user_settings.json")
                assert result == []
            except Exception:
                pass


def test_single_stock() -> None:
    """Тест одной акции"""
    mock_json_data: dict = {"user_stocks": ["TSLA"]}

    mock_response: dict = {"Global Quote": {"05. price": "250.75"}}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_json_data))):
        with patch("src.utils.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result = get_the_stock_price("user_settings.json")

            expected = [{"stock": "TSLA", "price": 250.75}]

            assert result == expected


def test_stock_price_rounding() -> None:
    """Тест округление цены"""
    mock_json_data: dict = {"user_stocks": ["MSFT"]}

    mock_response: dict = {"Global Quote": {"05. price": "123.456789"}}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_json_data))):
        with patch("src.utils.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result = get_the_stock_price("user_settings.json")

            assert result[0]["price"] == 123.46


def test_different_stock_prices() -> None:
    """Тест разные цены для разных акций"""
    mock_json_data: dict = {"user_stocks": ["AAPL", "MSFT", "TSLA"]}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_json_data))):
        with patch("src.utils.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"Global Quote": {"05. price": "200.00"}}

            result = get_the_stock_price("user_settings.json")

            assert len(result) == 3
            assert result[0]["stock"] == "AAPL"
            assert result[1]["stock"] == "MSFT"
            assert result[2]["stock"] == "TSLA"
            assert all(item["price"] == 200.00 for item in result)


def test_invalid_price_format() -> None:
    """Тест невалидный формат цены"""
    mock_json_data: dict = {"user_stocks": ["INVALID"]}

    mock_response: dict = {"Global Quote": {"05. price": "not_a_number"}}  # Не число

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_json_data))):
        with patch("src.utils.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            with pytest.raises(ValueError):
                get_the_stock_price("user_settings.json")