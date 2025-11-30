import pandas as pd
from src.services import cashback_analysis

from src.views import greetings_on_time


def get_period_from_file() -> str:
    """Берет последнюю дату из файла и возвращает период с начала месяца по эту дату"""
    df = pd.read_excel("../data/operations.xlsx", sheet_name="Отчет по операциям")
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

    # Берет максимальную дату из файла
    max_date = df["Дата операции"].max()

    # Возвращает максимальную дату как строку для функции
    result: str = max_date.strftime("%Y-%m-%d %H:%M:%S")
    return result


if __name__ == "__main__":
    # Получает дату для формирования периода
    file_date = get_period_from_file()

    # Передает эту дату в функцию
    result = greetings_on_time(file_date)
    print(result)

    cashback_result = cashback_analysis(
        file_path="../data/operations.xlsx",
        year=2019,
        month=4
    )
    print(cashback_result)
