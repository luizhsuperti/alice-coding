import logging
import pickle
import sys
import joblib

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import recall_score
from sklearn.model_selection import RandomizedSearchCV

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
        return minimal_cut

    def optimize_model(self, X_train, y_train):
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
        try:
            self.model = self.randomforest.fit(X, y.values.ravel())
        except:
            print('Something didnt work in the fit')

    def calculate_cutoff(self, x_test, y_test):
        logging.info('Calculate Cutoff')
        self.cutoff = self._calculate_optimal_cutoff(self.model, x_test,
                                    y_test)
        print('optimal threshold based on precision-recall:', self.cutoff)

    def predict(self, X):
        if not hasattr(self, 'model'):
            logging.error('No model!. #ERROR# FIT THE FUCKIN MODEL, MATE')
            sys.exit(1)

        result = np.where(
            self.model.predict_proba(X)[:, 1] >= self.cutoff, 'MEDIUM_RISK',
            'LOW_RISK')

        return result
