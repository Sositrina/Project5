import datetime
import logging
import os
from typing import Optional, Callable, Any

import pandas as pd

# Настройка логирования
log_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(os.path.join(log_dir, "app.log"), encoding="utf-8"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def save_report(func:Callable[..., Any]) -> Callable :
    """
    Декоратор для сохранения результатов функции в файл.
    Сохраняет возвращаемое значение функции в файл report.txt
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info("Вызов функции")
        os.makedirs("../reports", exist_ok=True)
        try:
            result = func(*args, **kwargs)
            if isinstance(result, pd.DataFrame):
                json_data = result.to_json(orient="records", indent=2, force_ascii=False)
            else:
                json_data = json.dumps(result, indent=2, ensure_ascii=False)
            with open("../reports/report.txt", "w", encoding="utf-8") as f:
                f.write(json_data)
            logger.info("Результат функции сохранён в reports/report.txt")
            return result
        except Exception as e:
            logger.error(f"Ошибка в декораторе save_report: {e}")
            raise

    return wrapper


@save_report
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца."""
    logger.info("Начало анализа")
    if date is None:
        date = datetime.datetime.now().strftime("%d.%m.%Y")
        logger.debug("Дата не указана")

    logger.debug("Преобразование даты")
    target_date = pd.to_datetime(date, format="%d.%m.%Y")
    start_date = target_date - pd.DateOffset(months=3)
    logger.info(f"Период анализа: с {start_date.strftime('%d.%m.%Y')} по {target_date.strftime('%d.%m.%Y')}")

    # Фильтрация по категории
    logger.debug("Фильтрация по категории")
    filtered_by_category = transactions[transactions["Категория"] == category].copy()
    logger.info(f"Найдено {len(filtered_by_category)} записей по категории '{category}'")

    # Преобразует даты
    logger.debug("Преобразование дат в datetime")
    filtered_by_category["Дата платежа"] = pd.to_datetime(filtered_by_category["Дата платежа"], format="%d.%m.%Y")

    # Фильтрует по датам
    logger.debug("Фильтрация по временному периоду")
    result = filtered_by_category[
        (filtered_by_category["Дата платежа"] >= start_date) & (filtered_by_category["Дата платежа"] <= target_date)
    ]
    logger.info("Анализ завершён")
    return result
