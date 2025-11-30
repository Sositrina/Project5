import pandas as pd

from src.reports import spending_by_category


def test_date_none() -> None:
    """Тест когда date is None"""
    test_data = pd.DataFrame({"Категория": ["Супермаркеты"], "Дата платежа": ["01.01.2024"], "Сумма операции": [-100]})

    result = spending_by_category(test_data, "Супермаркеты", None)
    assert isinstance(result, pd.DataFrame)


def test_category_not_found() -> None:
    """Тест когда категория не существует"""
    test_data = pd.DataFrame(
        {
            "Категория": ["Такси", "Рестораны"],
            "Дата платежа": ["01.12.2021", "15.12.2021"],
            "Сумма операции": [-100, -200],
        }
    )

    result = spending_by_category(test_data, "Несуществующая", "31.12.2021")
    assert len(result) == 0


def test_empty_dataframe() -> None:
    """Тест с пустым DataFrame"""
    empty_df = pd.DataFrame(columns=["Категория", "Дата платежа", "Сумма операции"])
    result = spending_by_category(empty_df, "Супермаркеты", "31.12.2021")
    assert len(result) == 0