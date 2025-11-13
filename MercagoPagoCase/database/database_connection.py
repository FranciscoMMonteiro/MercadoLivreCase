from google.cloud import bigquery
from google.oauth2 import service_account
import json
import os

def get_bigquery_client(config_path: str = "database/bd_connection_variables.json") -> bigquery.Client:
    """
    Reads the credentials from the JSON file and returns an authenticated BigQuery client.

    Parameters
    ----------
    config_path : str
        Path to the JSON file containing the service account credentials.

    Returns
    -------
    google.cloud.bigquery.Client
    """
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        service_account_info = json.load(f)

    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    client = bigquery.Client(credentials=credentials, project=service_account_info["project_id"])
    
    return client


