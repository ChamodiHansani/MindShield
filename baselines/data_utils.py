# baselines/data_utils.py
import os
import re
import unicodedata
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from .text_normalizer import normalize_text

from .config import (
    DATA_PATH, TEXT_COL_CANDIDATES, LABEL_COL_CANDIDATES,
    RANDOM_STATE, TEST_SIZE, VAL_SIZE
)

def _pick_existing_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError(f"None of these columns exist: {candidates}. Found: {df.columns.tolist()}")

def basic_clean_text(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    s = unicodedata.normalize("NFKC", s)
    s = s.lower().strip()
    # remove extra whitespace
    s = re.sub(r"\s+", " ", s)
    return s

def load_dataset(path: str = DATA_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at: {path}")

    df = pd.read_excel(path)
    text_col = _pick_existing_col(df, TEXT_COL_CANDIDATES)
    label_col = _pick_existing_col(df, LABEL_COL_CANDIDATES)

    df = df.dropna(subset=[text_col, label_col]).copy()
    df[label_col] = df[label_col].astype(str).str.strip()
    df = df[df[label_col].str.lower() != "nan"]
    df = df[df[label_col] != ""]

    # create clean_text if not already there
    if "clean_text" not in df.columns:
        df["clean_text"] = df[text_col].apply(normalize_text)

    # create numeric label if not already there
    if "label" not in df.columns:
        le = LabelEncoder()
        df["label"] = le.fit_transform(df[label_col])
        class_names = list(le.classes_)
    else:
        # if label exists, still try to get class names from Risk_Level if available
        if label_col in df.columns and label_col != "label":
            class_names = sorted(df[label_col].unique().tolist())
        else:
            # fallback
            class_names = None

    return df, class_names

def split_data(df):
    # Train / Val / Test with stratify (same idea as your notebook)
    X = df["clean_text"]
    y = df["label"]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y,
        test_size=(TEST_SIZE + VAL_SIZE),
        random_state=RANDOM_STATE,
        stratify=y
    )

    # Split temp into val and test (equal proportion if both are 0.10)
    val_ratio_of_temp = VAL_SIZE / (TEST_SIZE + VAL_SIZE)

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=(1 - val_ratio_of_temp),
        random_state=RANDOM_STATE,
        stratify=y_temp
    )

    return X_train, X_val, X_test, y_train, y_val, y_test
