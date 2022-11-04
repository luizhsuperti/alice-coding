"""
Load data and generate CSV files.
"""

import logging

from redshift_export import get_data_path
from redshift_export.interfaces.pipeline_step import PipelineStep


class DataExtraction(PipelineStep):


    def __init__(self, params_path: str = "params/extracting.yaml"):
        super().__init__(input_path=None, input_specs=None, output_path=None)
        self.di.config.load('extracting', params_path)
        self.params = self.di.config.params['extracting']
        self.env = self.params['env']
        self.files = self.params['files']
        assert self.env == 'local' or self.env == 'prod', "Only local or prod environments supported"

    def load(self) -> None:
        datasets = {}
        for var, meta in self.files.items():
            if 'sheet_id' in meta:
                datasets[var] = self.di.sheets.load(
                    sheet_id=meta['sheet_id'],
                    sheet_range=meta['sheet_range'],
                    sheet_name=meta['sheet_name'])
            else:
                if self.env == 'prod':
                    datasets[var] = self.di.redshift.run_sql_query(
                        get_queries_path(meta['query']))

                else:
                    datasets[var] = self.di.static.load(path=get_data_path(meta['input_path']),
                                                        specs=meta['specs'])
        self.datasets = datasets

    def transform(self) -> None:
        pass

    def save(self) -> None:
        if hasattr(self, 'datasets'):
            for var, meta in self.files.items():
                self.di.static.write(df=self.datasets[var], path=get_data_path(meta['output_path']))
        else:
            logging.error("Data not found! Load it first.")
