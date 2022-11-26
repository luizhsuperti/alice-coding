import json
import os

from dotenv import load_dotenv
from daly_comorbity import get_lib_path


class Credentials:

    def __init__(self, load_path: str = get_lib_path('.env')):
        self.load_path = load_path
        load_dotenv(load_path)

    SLACK_TOKEN = os.getenv('SLACK_TOKEN')

    HUBSPOT_KEY = os.getenv('HUBSPOT_KEY')

    POSTGRES_TOKEN = os.getenv('POSTGRES_TOKEN')
    POSTGRES_ENDPOINT = os.getenv('POSTGRES_ENDPOINT')
    POSTGRES_USER = os.getenv('POSTGRES_USER')

    REDSHIFT_TOKEN = os.getenv('REDSHIFT_TOKEN')
    REDSHIFT_ENDPOINT = os.getenv('REDSHIFT_ENDPOINT')
    REDSHIFT_USER = os.getenv('REDSHIFT_USER')

    try:
        with open(get_lib_path('google_sheets_credentials.json')) as read_file:
            GOOGLE_CERTIFICATE = json.load(read_file)
    except FileNotFoundError:
        GOOGLE_CERTIFICATE = None
