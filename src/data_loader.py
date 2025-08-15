import pandas as pd
from src.constants import CSV
from src.preprocessing import object_columns_to_category
from src.preprocessing import base_preprocess_datetime

# ! Hardcoded ! It's unclear why this list of columns is used.
from src.preprocessing import base_preprocess_datetime

def load_original_data_csv():
    return pd.read_csv(CSV)

def ld(p, yrs=None, chunksize=200_000):
    keep = [
        "Start_Time", "Severity",
        "City",
        "Weather_Condition", "Visibility(mi)", "Precipitation(in)",
        "Temperature(F)", "Wind_Speed(mph)",
        "Bump", "Crossing", "Street", "Description",
    ]

    # типы для экономии памяти
    dtype = {
        "Severity": "Int8",
        "Visibility(mi)": "float32",
        "Precipitation(in)": "float32",
        "Temperature(F)": "float32",
        "Wind_Speed(mph)": "float32",
        "City": "string",
        "Weather_Condition": "string",
        "Street": "string",
        "Description": "string",
        "Bump": "string",       # нормализуем позже
        "Crossing": "string",   # нормализуем позже
    }

    # если задано yrs — оставим последние N лет (по году)
    cut_year = None
    if yrs:
        try:
            cut_year = 2024 - int(yrs)   # у тебя проект 2016–2023, берём от 2023
        except Exception:
            cut_year = None

    parts = []
    # читаем по частям и сразу чистим
    for chunk in pd.read_csv(
        p,
        usecols=lambda c: c in keep,
        dtype=dtype,
        on_bad_lines="skip",
        chunksize=chunksize,
        low_memory=True,   # пусть парсер стримит, а не держит всё
    ):
        # время и базовые фильтры
        chunk["Start_Time"] = pd.to_datetime(chunk["Start_Time"], errors="coerce")
        chunk["Severity"] = pd.to_numeric(chunk["Severity"], errors="coerce")
        chunk = chunk.dropna(subset=["Start_Time", "Severity"])

        if cut_year is not None:
            y = chunk["Start_Time"].dt.year
            chunk = chunk[y >= cut_year]

        # лёгкая нормализация строк до категорий потом
        parts.append(chunk)

    if not parts:
        return pd.DataFrame(columns=keep)

    df = pd.concat(parts, ignore_index=True)

    # базовый препроцесс и выбросы
    df = base_preprocess_datetime(
        df,
        apply_outliers=True,
        outlier_cols=["Visibility(mi)", "Precipitation(in)", "Temperature(F)", "Wind_Speed(mph)"],
    )

    # строки -> lower + category (только нужные столбцы)
    df = object_columns_to_category(df, columns=["City", "Weather_Condition"])

    return df

