import json
import logging
import pandas as pd

# Настройка логирования
logger = logging.getLogger(__name__)


def cashback_analysis(file_path: str, year: int, month: int) -> str:
    """Анализирует выгодные категории кэшбека и возвращает результат"""
    logger.info(f"Начало анализа кэшбека.")

    try:
        # Чтение данных
        logger.info(f"Чтение файла")
        df = pd.read_excel(file_path)
        logger.info(f"Файл прочитан")

        # Преобразование дат
        logger.info("Преобразование колонки 'Дата операции' в datetime")
        df["Дата операции"] = pd.to_datetime(
            df["Дата операции"],
            format='%d.%m.%Y %H:%M:%S',
            errors='coerce'
        )
        logger.debug(f"Тип данных после первого преобразования: {df['Дата операции'].dtype}")

        # если первое не сработало
        if df["Дата операции"].dtype == 'object':
            logger.warning("Первое преобразование не сработало, применяем альтернативный метод")
            df["Дата операции"] = pd.to_datetime(
                df["Дата операции"].astype(str),
                dayfirst=True,
                errors='coerce'
            )
            logger.debug(f"Тип данных после альтернативного преобразования: {df['Дата операции'].dtype}")

        # Проверка некорректных дат
        invalid_dates = df["Дата операции"].isna().sum()
        if invalid_dates > 0:
            logger.warning(f"Обнаружено {invalid_dates} некорректных дат")

        # Фильтрация по дате
        logger.info(f"Фильтрация данных за {month}/{year}")
        filtered_data = df[
            (df["Дата операции"].dt.year == year) &
            (df["Дата операции"].dt.month == month)
            ]
        logger.info(f"Найдено записей за указанный период: {len(filtered_data)}")

        # Фильтрация по кэшбэку
        logger.info("Фильтрация операций с положительным кэшбэком")
        filtered_data = filtered_data[
            (filtered_data["Кэшбэк"] > 0)
        ]
        logger.info(f"Операций с кэшбэком: {len(filtered_data)}")

        # Фильтрация по расходным операциям
        logger.info("Фильтрация расходных операций (отрицательные суммы)")
        filtered_data = filtered_data[
            filtered_data["Сумма платежа"] < 0
            ]
        logger.info(f"Расходных операций с кэшбэком: {len(filtered_data)}")

        if len(filtered_data) == 0:
            logger.warning("Нет данных, соответствующих критериям фильтрации")
            return json.dumps({}, ensure_ascii=False, indent=4)

        # Группировка и расчет кэшбека
        logger.info("Группировка данных по категориям и расчет кэшбека")
        expenses_by_category = filtered_data.groupby("Категория")["Сумма платежа"].sum()
        cashback_by_category = abs(expenses_by_category) // 100

        # Формирование результата
        result = cashback_by_category.to_dict()
        logger.info(f"Рассчитан кэшбек для {len(result)} категорий: {list(result.keys())}")

        total_cashback = sum(result.values())
        logger.info(f"Общий кэшбек: {total_cashback} руб.")

        return json.dumps(result, ensure_ascii=False, indent=4)

    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при анализе кэшбека: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
