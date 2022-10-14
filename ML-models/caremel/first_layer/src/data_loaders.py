import pandas as pd
import pandas.io.sql as sqlio
import psycopg2
from config import Credentials
DEFAULT_POSTGRES_ENDPOINT = Credentials.POSTGRES_ENDPOINT
DEFAULT_POSTGRES_TOKEN = Credentials.POSTGRES_TOKEN
DEFAULT_POSTGRES_USER = Credentials.POSTGRES_USER
DEFUALT_REDSHIFT_ENDPOINT = Credentials.REDSHIFT_ENDPOINT
DEFAULT_REDSHIFT_TOKEN = Credentials.REDSHIFT_TOKEN
DEFAULT_REDSHIFT_USER = Credentials.REDSHIFT_USER

class ConnectionDataWarehouse:
    """
    A class used to stablish a connection, via Sagemaker endpoint,
    with Alice's PostgreSQL or Redshift data warehosue.
    Methods
    -------
    run_sql_query(query)
        Prints the animals name and what sound it makes
    """
    def __init__(self,
                 user: str = None,
                 dw: str = 'postgresql',
                 port: str = 'default',
                 region: str = 'us-east-1',
                 dbname: str = 'main'):
        """
        Parameters
        ----------
        user : str
            The user credential
        port: str
            AWS connection port
        region: str
            AWS connection region
        dbname:
            AWS database name
        """
        assert dw == 'postgresql' or dw == 'redshift', 'Only PostgreSQL or Redshift is supported'
        self.region = region
        self.dbname = dbname
        if dw == 'postgresql':
            self.user = (user if user else DEFAULT_POSTGRES_USER)
            self.endpoint = DEFAULT_POSTGRES_ENDPOINT
            self.token = DEFAULT_POSTGRES_TOKEN
            if port == 'default':
                self.port = '5432'
        if dw == 'redshift':
            self.user = (user if user else DEFAULT_REDSHIFT_USER)
            self.endpoint = DEFUALT_REDSHIFT_ENDPOINT
            self.token = DEFAULT_REDSHIFT_TOKEN
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