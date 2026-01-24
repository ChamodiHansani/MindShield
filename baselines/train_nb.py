# baselines/train_nb.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from .data_utils import load_dataset, split_data
from .eval_utils import evaluate_and_save
from .config import TFIDF_MAX_FEATURES, TFIDF_NGRAM_RANGE

def main():
    df, class_names = load_dataset()
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(df)

    vectorizer = TfidfVectorizer(max_features=TFIDF_MAX_FEATURES, ngram_range=TFIDF_NGRAM_RANGE)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = MultinomialNB()
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    evaluate_and_save("naive_bayes_tfidf", y_test, y_pred, class_names)

if __name__ == "__main__":
    main()
