import joblib
import os
import logging
import subprocess
import sys

if os.path.isfile(os.path.join(os.path.dirname(__file__), "requirements.txt")):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", \
        os.path.join(os.path.dirname(__file__), "requirements.txt"), \
        '--use-deprecated=legacy-resolver'])

if os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'model.py')):
    import model

def model_fn(model_dir):    
    logger = logging.getLogger()
    logger.info(f'File: {os.path.join(model_dir, "model.joblib")}')
    clf = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clf

# def input_fn(input_data, content_type):
#     return input_data

# def output_fn(prediction, accept):
#     return prediction

# def predict_fn(input_data, model):
#     return model.predict(input_data)