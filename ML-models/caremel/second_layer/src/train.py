import pandas as pd
from model import Model
class Train:

    def __init__(self) -> None:
        self.X = pd.read_csv("output/X.csv")
        self.y = pd.read_csv("output/y.csv")
        self.X_train = pd.read_csv("output/X_train.csv")
        self.X_test = pd.read_csv("output/X_test.csv")
        self.y_test = pd.read_csv("output/y_test.csv")
        self.y_train = pd.read_csv("output/y_train.csv")
        self.model = Model()
        pass

    def execute(self):
        self.model.optimize_model(self.X_train, self.y_train)
        self.model.fit(self.X_train, self.y_train)
        self.model.calculate_cutoff(self.X_test, self.y_test)
        self.model.save(path='output/')
        print("CareMel second layer trained and export into models")