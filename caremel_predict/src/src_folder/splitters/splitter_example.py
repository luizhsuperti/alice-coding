from $PROJECT_NAME$.interfaces.splitter import Splitter
from sklearn.model_selection import train_test_split


class DefaultSplitter(Splitter):

    def __init__(self, test_size: float = 0.2, random_state: int = 42):
        self.test_size = test_size
        self.random_state = random_state

    def split(self, X, y):
        return train_test_split(X,
                                y,
                                test_size=self.test_size,
                                random_state=self.random_state)
