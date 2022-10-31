from abc import ABC, abstractmethod

import joblib
from $PROJECT_NAME$ import get_models_path


class Transformer(ABC):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    @abstractmethod
    def transform(self, X):
        pass

    def inverse_transform(self, X):
        pass

    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X)

    def save(self):
        joblib.dump(self, get_models_path('{}.joblib'.format(self.__class__.__name__)))

    def load(self):
        return joblib.load(get_models_path('{}.joblib'.format(self.__class__.__name__)))
