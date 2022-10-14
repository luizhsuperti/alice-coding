from alice_data_lib.mlops.deploy import Deploy
import os

base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'src')
pipeline_execution = Deploy('caramelosecondlayer', base_dir, create_endpoint=True).create_pipeline().execute()



