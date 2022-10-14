import logging

import numpy as np
from $PROJECT_NAME$ import get_data_path
from $PROJECT_NAME$.interfaces.pipeline_step import PipelineStep
from $PROJECT_NAME$.interfaces.splitter import Splitter


class Splitting(PipelineStep):

    def __init__(self,
                 splitter: Splitter,
                 input_path: str,
                 input_specs: dict,
                 output_path=get_data_path(path=None),
                 params_path: str = "params/splitting.yaml",
                 splitter_args: dict = {}):
        super().__init__(input_path=input_path,
                         input_specs=input_specs,
                         output_path=output_path)
        self.splitter = splitter(**splitter_args)
        self.di.config.load('splitting', params_path)
        self.params = self.di.config.params['splitting']

    def transform(self) -> None:
        if not hasattr(self, 'data'):
            logging.error("Data not found! Load it first.")
        features = np.setdiff1d(
            self.data.columns,
            [self.params['id_column'], self.params['target_column']]).tolist()
        self.X = self.data[features]
        self.y = self.data[self.params['target_column']]
        self.X_train, self.X_test, self.y_train, self.y_test = self.splitter.split(
            self.X, self.y, **self.params)

    def save(self) -> None:
        self.di.static.write(self.X, self.output_path + 'X.csv')
        self.di.static.write(self.y, self.output_path + 'y.csv')
        self.di.static.write(self.X_train, self.output_path + 'X_train.csv')
        self.di.static.write(self.X_test, self.output_path + 'X_test.csv')
        self.di.static.write(self.y_train, self.output_path + 'y_train.csv')
        self.di.static.write(self.y_test, self.output_path + 'y_test.csv')
