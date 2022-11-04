"""
Preprocess data for training and testing.
"""

import logging

from redshift_export.interfaces.pipeline_step import PipelineStep


class DataPreprocessing(PipelineStep):

    def __init__(
            self,
            input_path="interim/lead_member_funnel_clean.csv",
            input_specs={
                'low_memory': False,
                'encoding': 'utf-8',
                'dtype': {
                    'member_postal_code_start': str
                }
            },
            output_path="interim/lead_member_funnel_preprocessed.csv",
            params_path="params/preprocessing.yaml"):
        super().__init__(input_path=input_path,
                         input_specs=input_specs,
                         output_path=output_path)
        self.di.config.load('preprocessing', params_path)
        self.params = self.di.config.params['preprocessing']
        self.dropper = Dropper(drop_columns=self.params['drop_columns'])
        self.renamer = Renamer(rename_meta=self.params['rename_meta'])
        self.binner = Binner(bins_cut_meta=self.params['bins_cut_meta'],
                             bins_qcut_meta=self.params['bins_qcut_meta'],
                             bins_other_meta=self.params['bins_other_meta'])
        self.missing_inputer = MissingInputer(
            default_numerical_missing_columns=self.
            params['default_numerical_missing_columns'],
            default_categorical_missing_columns=self.
            params['default_categorical_missing_columns'],
            other_missing_meta=self.params['other_missing_meta'],
            default_fill_meta=self.params['default_fill_meta'])
        self.mininum_percentage_filter = MinimumPercentageFilter(
            minimum_percentage_meta=self.params['minimum_percentage_meta'])
        self.binarizer = Binarizer(
            binarizer_meta=self.params['binarizer_meta'])
        self.encoder = Encoder(encoder_meta=self.params['encoder_meta'])
        self.transformer = Transformer(
            transformer_meta=self.params['transformer_meta'])
        self.custom_transformer = CustomTransformer()

    def transform(self) -> None:
        if hasattr(self, 'data'):
            self.data = self.dropper.transform(self.data)
            self.data = self.renamer.transform(self.data)
            self.data = self.binner.transform(self.data)
            self.data = self.missing_inputer.transform(self.data)
            self.data = self.mininum_percentage_filter.transform(self.data)
            self.data = self.binarizer.transform(self.data)
            self.data = self.encoder.transform(self.data)
            self.data = self.transformer.transform(self.data)
            self.data = self.custom_transformer.transform(self.data)
        else:
            logging.error("Data not found! Load it first.")
