# baselines/config.py
DATA_PATH = "data/MindShield_Dataset_9.xlsx"   
TEXT_COL_CANDIDATES = ["clean_text", "Text", "text"]
LABEL_COL_CANDIDATES = ["label", "Risk_Level", "risk_level"]

RANDOM_STATE = 42
TEST_SIZE = 0.10
VAL_SIZE = 0.10   # out of full data

TFIDF_MAX_FEATURES = 50000
TFIDF_NGRAM_RANGE = (1, 2)
