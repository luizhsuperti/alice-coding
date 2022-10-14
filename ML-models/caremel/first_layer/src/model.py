#standard packages
import pandas as pd
import numpy as np
import logging
import sys
#machine-learning packages
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import recall_score
import joblib

class GeneralModel:
    def __init__(self, path):
        filepath = path + 'model.joblib'
        self = joblib.load(filepath)

    def save(self, path: str):
        if not hasattr(self, 'model'):
            logging.error('No model!. #ERROR# FIT THE FUCKIN MODEL, MATE')
            sys.exit(1)
        logging.info('Save Model')
        filepath = path + 'model.joblib'
        joblib.dump(self, filepath)
        

class Model(GeneralModel):
    def __init__(self):
        self.randomforest = RandomForestClassifier(criterion='entropy')

    def _calculate_optimal_cutoff(self, estimator, X, y):
        all_f_scores = {}
        for i in np.arange(0, 100, 1, dtype=float):
            y_pred = np.where(
                estimator.predict_proba(X)[:, 1] >= (i / 100), 1, 0)
            immersion_rate = y_pred.mean()
            recall_v = recall_score(y, y_pred)
            immersion_adj_f_score = (1 + 1.0**2) * (
                (1 - immersion_rate) *
                (recall_v)) / ((1.0**2) * (1 - immersion_rate) + (recall_v))

            all_f_scores.update({i: immersion_adj_f_score})

        max_adj_fscore = max(all_f_scores.values())  # maximum value
        optimal_cutoff = [
            k for k, v in all_f_scores.items() if v == max_adj_fscore
        ]

        minimal_cut = min(optimal_cutoff) / 100
        print('optimal threshold for the first layer:', minimal_cut)
        return minimal_cut

    def _immersion_f_score(self, estimator, X, y):

        all_f_scores = {}
        for i in np.arange(0, 100, 1, dtype=float):

            y_pred = np.where(
                estimator.predict_proba(X)[:, 1] >= (i / 100), 1, 0)
            immersion_rate = y_pred.mean()
            recall_v = recall_score(y, y_pred)
            immersion_adj_f_score = (1 + 1.0**2) * (
                (1 - immersion_rate) *
                (recall_v)) / ((1.0**2) * (1 - immersion_rate) + (recall_v))

            all_f_scores.update({i: immersion_adj_f_score})

        max_adj_fscore = max(all_f_scores.values())  # maximum value
        return max_adj_fscore

    def optimize(self, X_train, y_train):
        logging.info('Optimize Model')
        param_grid = {
            'max_depth': [4, 8],
            'max_features': ['sqrt'],
            'n_estimators': [25],
            'min_samples_leaf': [2],
            'min_samples_split': [2],
            'ccp_alpha': [0.01]
        }
        randomforest_search = RandomizedSearchCV(
            estimator=self.randomforest,
            param_distributions=param_grid,
            n_iter=125,
            cv=4,
            verbose=0,
            scoring=self._immersion_f_score)
        randomforest_search.fit(X_train, y_train.values.ravel())
        best_params = randomforest_search.best_estimator_
        self.randomforest = best_params

    def fit(self, X, y):
        logging.info('Fit Model')
        try:
            self.model = self.randomforest.fit(X, y.values.ravel())
        except Exception as e:
            print(f'Something didnt work in the fit {e}')
            raise Exception(e)
    
    def calculate_cutoff(self, x_test, y_test):
        logging.info('Calculate Cutoff')
        self.cutoff = self._calculate_optimal_cutoff(self.model, x_test,
                                    y_test)

    def predict(self, X):
        if not hasattr(self, 'model'):
            logging.error('No model!. #ERROR# FIT THE FUCKIN MODEL, MATE')
            sys.exit(1)

        self.last_result = np.where(
            self.model.predict_proba(X)[:, 1] >= self.cutoff, 'LOW_RISK', 'NO_RISK')

        return self.last_result