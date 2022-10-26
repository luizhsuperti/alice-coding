import json
import os

from dotenv import load_dotenv
from carai import get_lib_path
load_dotenv(get_lib_path('.env'))

class Credentials:
    def __init__(self):
        pass
    SLACK_TOKEN = os.getenv('SLACK_TOKEN')
    HUBSPOT_KEY = os.getenv('HUBSPOT_KEY')
    POSTGRES_TOKEN = os.getenv('POSTGRES_TOKEN')
    POSTGRES_ENDPOINT = os.getenv('POSTGRES_ENDPOINT')
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    REDSHIFT_TOKEN = os.getenv('REDSHIFT_TOKEN')
    REDSHIFT_ENDPOINT = os.getenv('REDSHIFT_ENDPOINT')
    REDSHIFT_USER = os.getenv('REDSHIFT_USER')
    AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')
    try:
        with open(get_lib_path('google_sheets_credentials.json')) as read_file:
            GOOGLE_CERTIFICATE = json.load(read_file)
    except FileNotFoundError:
        GOOGLE_CERTIFICATE = None