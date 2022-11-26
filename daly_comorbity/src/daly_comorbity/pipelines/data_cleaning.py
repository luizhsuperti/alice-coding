"""
Clean data and apply basic transformations.
"""

import logging

from daly_comorbity.interfaces.pipeline_step import PipelineStep
from daly_comorbity.transformers.cleaners import Cleaner, Filter


class DataCleaning(PipelineStep):

    def __init__(
            self,
            input_path="interim/low_cost_leads_funnel.csv",
            input_specs={
                'low_memory': False,
                'encoding': 'utf-8',
                'dtype': {
                    'member_postal_code_start': str
                }
            },
            output_path='interim/low_cost_leads_funnel_clean.csv',
            params_path="params/cleaning.yaml"):
        super().__init__(input_path=input_path,
                         input_specs=input_specs,
                         output_path=output_path)
        self.di.config.load('cleaning', params_path)
        self.params = self.di.config.params['cleaning']
        self.cleaner = Cleaner(
            variable_columns=self.params['variable_columns'],
            duplicate_columns=self.params['duplicate_columns'])
        self.filter = Filter(
            filter_notnull_columns=self.params['filter_notnull_columns'],
            filter_other_columns=self.params['filter_other_columns'])

    def transform(self) -> None:
        if hasattr(self, 'data'):
            self.data = self.cleaner.transform(self.data)
            self.data = self.filter.transform(self.data)

        else:
            logging.error("Data not found! Load it first.")
