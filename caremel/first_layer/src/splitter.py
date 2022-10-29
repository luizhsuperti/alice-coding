import logging
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


class Splitter:

    def __init__(self, data, target_column=None, id_column=None, test_size=None):
        self.data = data
        self.target_column = target_column
        self.id_column = id_column
        self.test_size = test_size

    def split(self):
        if not hasattr(self, 'data'):
            logging.error('No data!. #ERROR# LOAD THE FUCKIN DATA, MATE')
            sys.exit(1)
        features = np.setdiff1d(self.data.columns,
                                [self.target_column, self.id_column])
        self.X = self.data[features]
        self.y = self.data[self.target_column]
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=self.test_size)
        return self.X, self.y, self.X_train, self.X_test, self.y_train, self.y_test

    def save(self):
        if not hasattr(self, 'X'):
            logging.error('No X data!. #ERROR# SPLIT THE FUCKIN DATA, MATE')
            sys.exit(1)
        self.X.to_csv('output/X.csv', index=False)
        self.y.to_csv('output/y.csv', index=False)
        self.X_train.to_csv('output/X_train.csv', index=False)
        self.X_test.to_csv('output/X_test.csv', index=False)
        self.y_train.to_csv('output/y_train.csv', index=False)
        self.y_test.to_csv('output/y_test.csv', index=False)
