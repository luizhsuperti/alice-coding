import logging
import os
import zipfile
import subprocess
import sys
import shutil
import inspect

class PipelineBootstrap:

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.parent_path = os.path.dirname(self.path)
        self.zip_path = self._get_zip_path()

    def _get_zip_path(self):
        if os.getenv("TASK") == 'train':
            return os.path.join(os.getenv("SM_INPUT_DIR", '/opt/ml/input'), 'data/files')
        else:
            return self.parent_path

    def set_workdir(self):
        os.chdir(self.path)
        return self

    def extract_files(self):
        with zipfile.ZipFile(os.path.join(self.zip_path, 'src.zip'), 'r') as zip_ref:
            zip_ref.extractall(self.path)
        return self

    def get_output_folder(self):
        if os.getenv("TASK") == 'train':
            output_dir = os.path.join(self.path, 'output')
            if os.path.isdir(output_dir):
                shutil.rmtree(output_dir)
            shutil.copytree(os.path.join(os.getenv("SM_INPUT_DIR", '/opt/ml/input'), 'data/preprocess'), output_dir)
        return self

    def install_pip(self):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", os.path.join(self.path, "requirements.txt"), '--use-deprecated=legacy-resolver'])
        return self

    def set_enviroment_vars(self):
        from alice_data_lib.mlops.enviroment import Enviroment
        Enviroment.set_enviroment_using_secret('AmazonSageMaker-dw-role')
        return self

    def run_task(self):
        if os.getenv("TASK") == 'preprocess':
            import preprocess
            if len(list(filter(lambda item: item[0] == 'Preprocess', inspect.getmembers(preprocess)))):
                preprocess.Preprocess().execute()
        elif os.getenv("TASK") == 'train':
            import train
            if len(list(filter(lambda item: item[0] == 'Train', inspect.getmembers(train)))):
                train.Train().execute()
            shutil.copy(os.path.join(self.path, 'output', 'model.joblib'), os.path.join(os.getenv('SM_MODEL_DIR', '/opt/ml/model'), 'model.joblib'))
        return self
    
    def execute(self):
        self.set_workdir() \
            .extract_files() \
            .get_output_folder() \
            .install_pip() \
            .set_enviroment_vars() \
            .run_task()

if __name__ == '__main__':
    PipelineBootstrap().execute()


