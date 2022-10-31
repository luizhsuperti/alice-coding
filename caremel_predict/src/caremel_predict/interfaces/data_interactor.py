import pandas as pd
import pandas.io.sql as sqlio
import psycopg2
import yaml
from caremel_predict import get_data_path
from caremel_predict.interfaces.config import Credentials
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


class WarehouseDataInteractor:
    """
    A class used to stablish a connection, via Sagemaker endpoint, with Alice's PostgreSQL or Redshift data warehouse.
    
    Methods
    -------
    run_sql_query(sql_path: str) -> pd.DataFrame
        Run a sql query file on the data warehouse.
    run_str_query(query: str) -> pd.DataFrame
        Execute a query text on the data warehouse.
    delete_table(table_name: str)
        Delete a table from the data warehouse.
    insert_table(table_name: str, data: pd.DataFrame, delete: bool = True)
        Insert a table into the data warehouse.
    
    Attributes
    ----------
    dw: str
        The data warehouse to connect to. Only PostgreSQL or Redshift is supported.
    port: str
        The port to connect to the data warehouse.
    region: str
        The region where the data warehouse is located.
    dbname: str
        The name of the database to connect to.
    """

    def __init__(self,
                 user: str = None,
                 dw: str = 'postgres',
                 port: str = 'default',
                 region: str = 'us-east-1',
                 dbname: str = 'main'):

        assert dw == 'postgres' or dw == 'redshift', 'Only PostgreSQL or Redshift is supported'
        self.user = user
        self.region = region
        self.dbname = dbname
        if dw == 'postgres':
            self.user = Credentials().POSTGRES_USER
            self.endpoint = Credentials().POSTGRES_ENDPOINT
            self.token = Credentials().POSTGRES_TOKEN
            if port == 'default':
                self.port = '5432'
        if dw == 'redshift':
            self.user = Credentials().REDSHIFT_USER
            self.endpoint = Credentials().REDSHIFT_ENDPOINT
            self.token = Credentials().REDSHIFT_TOKEN
            if port == 'default':
                self.port = '5439'

    def run_sql_query(self, sql_path: str) -> pd.DataFrame:
        """"
        Run a sql query file on the data warehouse.
        """
        query = open(sql_path, 'r').read()
        conn = psycopg2.connect(host=self.endpoint,
                                port=self.port,
                                database=self.dbname,
                                user=self.user,
                                password=self.token)
        data = sqlio.read_sql_query(query, conn)
        conn.close()
        return data

    def run_str_query(self, query: str) -> pd.DataFrame:
        """
        Execute a query text on the data warehouse.
        """
        conn = psycopg2.connect(host=self.endpoint,
                                port=self.port,
                                database=self.dbname,
                                user=self.user,
                                password=self.token)
        data = sqlio.read_sql_query(query, conn)
        conn.close()
        return data

    def _sql_execute(self, query: str):
        conn = psycopg2.connect(host=self.endpoint,
                                port=self.port,
                                database=self.dbname,
                                user=self.user,
                                password=self.token)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        conn.close()

    def delete_table(self, table_name: str):
        """
        Delete a table from the data warehouse.
        """
        query = f"DROP TABLE IF EXISTS {table_name}"
        self._sql_execute(query)

    def insert_table(self,
                     table_name: str,
                     data: pd.DataFrame,
                     delete: bool = True):
        """
        Insert a table into the data warehouse.
        """
        if delete:
            self.delete_table(table_name)
        query = f"CREATE TABLE {table_name} ({data.to_csv(index=False)})"
        self._sql_execute(query)


class RSWarehouseDataInteractor(WarehouseDataInteractor):

    def __init__(self):
        super().__init__(Credentials().REDSHIFT_USER, 'redshift')


class PGWarehouseDataInteractor(WarehouseDataInteractor):

    def __init__(self):
        super().__init__(Credentials().POSTGRES_USER, 'postgres')


class StaticDataInteractor:

    def __init__(self):
        self.cache_dict = {}

    def load(self, path, specs={}, refresh=False):
        cache_id = path + str(specs)
        if cache_id in self.cache_dict.keys() and not refresh:
            return self.cache_dict[cache_id]
        else:
            print("Loading fresh... File {}".format(path))
            df = pd.read_csv(get_data_path(path), **specs)
            self.cache_dict[cache_id] = df
            return df

    def write(self, df, path):
        df.to_csv(get_data_path(path), index=False, encoding='utf-8')


class GoogleSheetsDataInteractor:

    def __init__(self, GOOGLE_CERTIFICATE=Credentials().GOOGLE_CERTIFICATE):
        """
        Create the object with a sheet_id and the path to the json file containing the key
        """
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = ServiceAccountCredentials().from_json_keyfile_dict(
            GOOGLE_CERTIFICATE, scopes)

    def load(self, sheet_id, sheet_range, sheet_name=None):
        sheet_range = '{}!{}'.format(
            sheet_name, sheet_range) if sheet_name else sheet_range
        service = build('sheets', 'v4', credentials=self.credentials)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id,
                                    range=sheet_range).execute()

        values = result.get('values', [])
        df_results = pd.DataFrame(values[1:], columns=values[0])

        return df_results


class BucketDataInteractor:

    def __init__(self):
        self.cache_dict = {}
        self.AWS_ACCESS_KEY_ID = Credentials().AWS_ACCESS_KEY_ID
        self.AWS_SECRET_ACCESS_KEY = Credentials().AWS_SECRET_ACCESS_KEY
        self.AWS_SESSION_TOKEN = Credentials().AWS_SESSION_TOKEN
        self.AWS_BUCKET_NAME = Credentials().AWS_BUCKET_NAME

    def load(self, path, specs={}, refresh=False):
        cache_id = path + str(specs)
        if cache_id in self.cache_dict.keys() and not refresh:
            return self.cache_dict[cache_id]
        else:
            print("Loading fresh... File {}".format(path))
            if path.endswith('.csv'):
                df = pd.read_csv(f"s3://{self.AWS_S3_BUCKET}/{path}",
                                 **specs,
                                 storage_options={
                                     'key': self.AWS_ACCESS_KEY_ID,
                                     'secret': self.AWS_SECRET_ACCESS_KEY,
                                     'token': self.AWS_SESSION_TOKEN,
                                 })
            elif path.endswith('.json'):
                df = pd.read_json(f"s3://{self.AWS_S3_BUCKET}/{path}",
                                  **specs,
                                  orient="index",
                                  storage_options={
                                      'key': self.AWS_ACCESS_KEY_ID,
                                      'secret': self.AWS_SECRET_ACCESS_KEY,
                                      'token': self.AWS_SESSION_TOKEN,
                                  }).to_dict()[0]
            self.cache_dict[cache_id] = df
            return df

    def write(self, df, path):
        df.to_csv(f"s3://{self.AWS_S3_BUCKET}/{path}",
                  index=False,
                  encoding='utf-8',
                  storage_options={
                      'key': self.AWS_ACCESS_KEY_ID,
                      'secret': self.AWS_SECRET_ACCESS_KEY,
                      'token': self.AWS_SESSION_TOKEN,
                  })


class ConfigDataInteractor:

    def __init__(self):
        self.params = {}

    def load(self, name, path):
        with open(get_data_path(path), 'r') as f:
            params = yaml.load(f, Loader=yaml.FullLoader)
            self.params[name] = params
        return params

    def write(self, data, path):
        with open(get_data_path(path), 'w') as f:
            yaml.dump(data, f)


class DataInteractor:

    def __init__(self):
        self.static = StaticDataInteractor()
        self.sheets = GoogleSheetsDataInteractor()
        self.postgres = PGWarehouseDataInteractor()
        self.redshift = RSWarehouseDataInteractor()
        self.bucket = BucketDataInteractor()
        self.config = ConfigDataInteractor()
