import datetime
import json
import logging
from typing import Any, Dict, List

import pandas as pd
import requests
from pandas import DataFrame
from dotenv import load_dotenv
import os

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log", encoding="utf-8"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


URL = "https://api.apilayer.com/exchangerates_data/convert"
API_KEY = os.getenv("API_KEY")

API_KEY_STOCK = os.getenv("API_KEY_STOCK")
URL_STOCK = "https://www.alphavantage.co/query"


def timed_message() -> str:
    """Возвращает «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи» в зависимости от текущего времени."""
    # Узнает время по часам
    logger.info("Начало работы функции timed_message")
    time_hour = datetime.datetime.now().hour
    logger.debug(f"Текущий час: {time_hour}")

    if 0 <= time_hour < 4:
        result = "Доброй ночи"
    elif 4 <= time_hour < 12:
        result = "Доброе утро"
    elif 12 <= time_hour < 16:
        result = "Добрый день"
    else:
        result = "Добрый вечер"

    logger.info(f"Функция timed_message возвращает: {result}")
    return result


def get_data_time(data_time: str) -> list[str]:
    """Возвращает дату и время в формате YYYY-MM-DD HH:MM:SS"""
    # Пеобразует строку в объект
    logger.info(f"Функция get_data_time вызвана с параметром: {data_time}")
    dt = datetime.datetime.strptime(data_time, "%Y-%m-%d %H:%M:%S")

    try:
        dt = datetime.datetime.strptime(data_time, "%Y-%m-%d %H:%M:%S")
        logger.debug(f"Дата преобразована: {dt}")

        start_of_month = dt.replace(day=1)
        result = [start_of_month.strftime("%d.%m.%Y %H:%M:%S"), dt.strftime("%d.%m.%Y %H:%M:%S")]

        logger.info(f"Функция get_data_time возвращает: {result}")
        return result

    except ValueError as e:
        logger.error(f"Ошибка преобразования даты: {e}")
        raise


def get_path_and_period(path_to_file: str, period_date: list) -> DataFrame:
    """Возвращает дату за период"""
    logger.info(f"Функция get_path_and_period вызвана. Файл: {path_to_file}, период: {period_date}")
    try:
        df = pd.read_excel(path_to_file, sheet_name="Отчет по операциям")
        logger.info(f"Файл прочитан. Количество строк: {len(df)}")

        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
        logger.debug("Даты преобразованы в datetime")

        start_date = datetime.datetime.strptime(period_date[0], "%d.%m.%Y %H:%M:%S")
        end_date = datetime.datetime.strptime(period_date[1], "%d.%m.%Y %H:%M:%S")
        logger.debug(f"Период фильтрации: с {start_date} по {end_date}")

        filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]

        result = filtered_df.sort_values(by="Дата операции", ascending=True)
        logger.info(f"После фильтрации осталось {len(result)} строк")

        return result

    except FileNotFoundError:
        logger.error(f"Файл не найден: {path_to_file}")
        raise
    except Exception as e:
        logger.error(f"Ошибка в get_path_and_period: {e}")
        raise


def take_the_card_number(sorted_df: DataFrame) -> list[dict]:
    """Принимает DataFrame и возвращает список"""
    logger.info("Функция take_the_card_number вызвана")

    if len(sorted_df) == 0:
        logger.warning("Передан пустой DataFrame")
        return []

    list_card = []
    logger.info(f"Обработка {len(sorted_df)} карт")

    for index, row in sorted_df.iterrows():
        last_number = str(row["Номер карты"]).replace("*", "")
        total_amount = row["Сумма операции с округлением"]
        cashback = total_amount // 100

        list_card.append({"last_digits": last_number, "total_spent": total_amount, "cashback": cashback})

        logger.debug(f"Карта {last_number}: сумма {total_amount}, кэшбэк {cashback}")

    logger.info(f"Функция возвращает {len(list_card)} карт")
    return list_card


def top_transactions(sorted_df: DataFrame, get_top: int) -> List[Dict[str, Any]]:
    """Принимает DataFrame и возвращает топ 5 транзакций по сумме платежей"""
    logger.info(f"Функция top_transactions вызвана. Запрошено топ {get_top} транзакций")

    top_sum_transactions = []
    sorted_sum_df = sorted_df.sort_values(by="Дата операции", ascending=False)
    logger.debug("DataFrame отсортирован по дате операции")

    top_transactions_df = sorted_sum_df.head(get_top)
    logger.info(f"Выбрано {len(top_transactions_df)} транзакций из {len(sorted_df)}")

    transactions_sorted = top_transactions_df[["Дата платежа", "Сумма операции", "Категория", "Описание"]]

    for index, row in transactions_sorted.iterrows():
        transaction = {
            "date": row["Дата платежа"],
            "amount": row["Сумма операции"],
            "category": row["Категория"],
            "description": row["Описание"],
        }
        top_sum_transactions.append(transaction)
        logger.debug(f"Добавлена транзакция: {transaction}")

    logger.info(f"Функция возвращает {len(top_sum_transactions)} транзакций")
    return top_sum_transactions


def get_a_curse(path_user_json: str) -> list[dict]:
    """Принимает данные из файла user_settings.json и возвращает курс валют"""
    logger.info(f"Функция get_a_curse вызвана для файла: {path_user_json}")
    currency_rates = []

    try:
        with open(path_user_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            currencies = data["user_currencies"]
            logger.info(f"Найдены валюты: {currencies}")

            for currency in currencies:
                logger.info(f"Запрос курса для валюты: {currency}")

                payload = {"amount": 1, "from": currency, "to": "RUB"}
                headers = {"apikey": API_KEY}

                response = requests.request("GET", URL, headers=headers, params=payload)
                status_code = response.status_code
                logger.debug(f"API ответ: статус {status_code}")

                if status_code == 200:
                    result = response.json()
                    currency_code_response = result["query"]["from"]
                    currency_amount = round(result["result"], 2)

                    currency_rates.append({"currency": currency_code_response, "rate": str(currency_amount)})

                    logger.info(f"Курс {currency}: {currency_amount} RUB")
                else:
                    logger.warning(f"Ошибка API для валюты {currency}: статус {status_code}")

        logger.info(f"Функция возвращает курсы для {len(currency_rates)} валют")
        return currency_rates

    except FileNotFoundError:
        logger.error(f"Файл не найден: {path_user_json}")
        raise
    except Exception as e:
        logger.error(f"Ошибка в get_a_curse: {e}")
        raise


def get_the_stock_price(path_user_json: str) -> list[dict]:
    """Возвращает сумму акций"""
    logger.info(f"Функция get_the_stock_price вызвана для файла: {path_user_json}")
    stock_rates = []

    try:
        with open(path_user_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            stocks = data["user_stocks"]
            logger.info(f"Найдены акции: {stocks}")

            for stock in stocks:
                logger.info(f"Запрос цены для акции: {stock}")

                url = f"{URL_STOCK}?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY_STOCK}"
                response = requests.get(url)

                if response.status_code == 200:
                    api_data = response.json()

                    if "Global Quote" in api_data and "05. price" in api_data["Global Quote"]:
                        price = api_data["Global Quote"]["05. price"]
                        price_float = round(float(price), 2)

                        stock_rates.append({"stock": stock, "price": price_float})

                        logger.info(f"Цена акции {stock}: {price_float}")
                    else:
                        logger.warning(f"Некорректный ответ API для акции {stock}")
                else:
                    logger.warning(f"Ошибка API для акции {stock}: статус {response.status_code}")

        logger.info(f"Функция возвращает цены для {len(stock_rates)} акций")
        return stock_rates

    except FileNotFoundError:
        logger.error(f"Файл не найден: {path_user_json}")
        raise
    except Exception as e:
        logger.error(f"Ошибка в get_the_stock_price: {e}")
        raise