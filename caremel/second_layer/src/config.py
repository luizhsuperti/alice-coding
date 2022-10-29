import json
import os

from dotenv import load_dotenv

load_dotenv("/root/machine_learning/users/luiz_superti/lib/.env")


class Credentials:
    """
    Class to handle credentials.
    """
    SLACK_TOKEN = os.getenv('SLACK_TOKEN')

    HUBSPOT_KEY = os.getenv('HUBSPOT_KEY')

    CEP_ABERTO_KEY = os.getenv('CEP_ABERTO_KEY')

    POSTGRES_TOKEN = os.getenv('POSTGRES_TOKEN')
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_ENDPOINT = os.getenv('POSTGRES_ENDPOINT')

    REDSHIFT_TOKEN = os.getenv('REDSHIFT_TOKEN')
    REDSHIFT_USER = os.getenv('REDSHIFT_USER')
    REDSHIFT_ENDPOINT = os.getenv('REDSHIFT_ENDPOINT')

   # with open('src/data/google_sheets_credentials.json') as read_file:
    #    GOOGLE_CERTIFICATE = json.load(read_file)