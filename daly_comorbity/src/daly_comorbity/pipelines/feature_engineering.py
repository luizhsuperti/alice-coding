"""
Feature engineering for the model.
"""

import logging

from daly_comorbity.interfaces.pipeline_step import PipelineStep
from daly_comorbity.transformers.feature_engineers import (Dumminizer, Scaler,
                                                           Selector)


class FeatureEngineering(PipelineStep):

    def __init__(
            self,
            input_path="interim/lead_member_funnel_preprocessed.csv",
            input_specs={
                'low_memory': False,
                'encoding': 'utf-8',
                'dtype': {
                    'member_postal_code_start': str
                }
            },
            output_path="interim/lead_member_funnel_feature_engineered.csv",
            params_path="params/feature_engineering.yaml"):
        super().__init__(input_path=input_path,
                         input_specs=input_specs,
                         output_path=output_path)
        self.di.config.load('feature_engineering', params_path)
        self.params = self.di.config.params['feature_engineering']
        self.selector = Selector(
            selection_drop_columns=self.params['selection_drop_columns'])
        self.dumminizer = Dumminizer(
            dummies_columns=self.params['dummies_columns'])
        self.scaler = Scaler(scale_columns=self.params['scale_columns'])

    def transform(self, X):
        if hasattr(self, 'data'):
            X = self.selector.transform(X)
            X = self.dumminizer.transform(X)
            X = self.scaler.transform(X)
            return X
        else:
            logging.error("Data not found! Load it first.")
