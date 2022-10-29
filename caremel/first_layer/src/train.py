#standard packages
import pandas as pd
import numpy as np
import logging
import sys
#machine-learning packages
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import recall_score
from model import Model

class Train:

    def __init__(self):
        self.X = pd.read_csv("output/X.csv")
        self.y = pd.read_csv("output/y.csv")
        self.X_train = pd.read_csv("output/X_train.csv")
        self.X_test = pd.read_csv("output/X_test.csv")
        self.y_test = pd.read_csv("output/y_test.csv")
        self.y_train = pd.read_csv("output/y_train.csv")
        self.model = Model()
        

    def execute(self):
        logging.info('Training Model')
        self.model.optimize(self.X_train, self.y_train)
        self.model.fit(self.X_train, self.y_train)
        self.model.calculate_cutoff(self.X_test, self.y_test)
        self.model.save(path='output/')
        print("CareMel first layer trained and export into output")