from abc import ABC, abstractmethod
from $PROJECT_NAME$.interfaces.data_interactor import DataInteractor


class PipelineStep(ABC):

    def __init__(self, input_path: str, input_specs: dict, output_path: str):
        self.di = DataInteractor()
        self.input_path = input_path
        self.input_specs = input_specs
        self.output_path = output_path

    def load(self) -> None:
        self.data = self.di.static.load(self.input_path, self.input_specs)

    @abstractmethod
    def transform(self) -> None:
        pass

    def save(self) -> None:
        self.di.static.write(self.data, self.output_path)
        return self.output_path

    def execute(self) -> None:
        self.load()
        self.transform()
        self.save()