   
from sklearn.feature_extraction.text import TfidfVectorizer


def build_vectorizer() -> TfidfVectorizer:
                                              
    return TfidfVectorizer(
        strip_accents="unicode",
        analyzer="word",
        max_features=10_000,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )


def fit_and_transform(vectorizer: TfidfVectorizer, X_train, X_test):
           
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    return X_train_vec, X_test_vec
