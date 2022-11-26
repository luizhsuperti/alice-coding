# Google Sheets

Esse markdown tem como objetivo ensinar e fornecer as ferramentas necessárias para que seja possível importar planilhas no Google Sheets no Python como um DataFrame.

## 1) Criar o arquivo .json com as credenciais

Basta copiar o conteúdo do arquivo _google_sheets_key.json_ em um arquivo JSON com nome de sua escolha

## 2) Compartilhar o sheets que deseja ler com o email credenciado

Copiar o email _airflow-service@airflow-sheets-i-1608230591403.iam.gserviceaccount.com_

```python:
%pip install oauth2client
%pip install googleapi
```

```python:
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import json
import pandas as pd
```

## 3) Copiar o ID do Google Sheets e definir o range do sheets desejado na leitura

O ID está na url da planilha, depois da tag /d/. Substituir na variável _sheet_id_.

Além disso, basta definir a variável _sheet_range_ como a porção da planilha que será lida pelo código, por exemplo "A1:Z999" para selecionar todas as linhas de A a Z.

## 4) Instanciar a classe e ler a planilha

Com todas as informações definidas, basta instanciar a classe e realizar a leitura por meio da função _read_sheets_ como mostrado no exemplo abaixo.

```python:
class GoogleSheetsDataInteractor:

    def __init__(self, GOOGLE_CERTIFICATE=DEFAULT_GOOGLE_CERTIFICATE):
        """
        Create the object with a sheet_id and the path to the json file containing the key
        """
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
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
```

## 5) Exemplo de uso

```python
sheet_id = '1Dbp69Fr3VxYA_JHO0glgvIZBI2G5HX5SoskAK6ztr1w'
sheet_range = 'A1:Z9999'

db_sheets = ConnectionGoogleSheets()
df = db_sheets.read_sheets(sheet_id, sheet_range)
df.head()
```