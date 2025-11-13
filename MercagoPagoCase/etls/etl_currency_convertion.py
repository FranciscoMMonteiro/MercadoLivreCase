import requests
from dotenv import load_dotenv
import os
import json
from utils.token_functions import generate_new_tokens, update_env_token
from utils.api_fuctions import search_product_id, search_product_name 
from utils.api_fuctions import get_items, get_currency_convertion
from utils.api_fuctions import get_sellers, get_items_sold
with open("site_ids.json", "r", encoding="utf-8") as f:
    site_ids = json.load(f)
from config import COUNTRY, STATUS_ID, PAGING_LIMIT,CONDITION
import pandas as pd
import time
from datetime import datetime
from database.database_connection import get_bigquery_client
from google.cloud import bigquery


def main():
    load_dotenv('.env')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

    get_new_token = input('Do you want to get a new refresh token? (y/n): ')
    if get_new_token.lower() == 'y':
        new_access_token, new_refresh_token = generate_new_tokens(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
        update_env_token('ACCESS_TOKEN',new_access_token)
        update_env_token('REFRESH_TOKEN',new_refresh_token)
        ACCESS_TOKEN = new_access_token
        REFRESH_TOKEN = new_refresh_token

    currency_data = {
        'from_currency_id':[],
        'to_currency_id':[],
        'rate':[],
        'rate_date':[]
    }

    bigquery_client = get_bigquery_client()
    query = """
        SELECT *
        FROM `mercadolivrecase.items`
    """

    df_items = bigquery_client.query(query).to_dataframe()
    currency_list = list(df_items['currency_id'].unique())

    for currency in currency_list:
        status, convertion = get_currency_convertion(currency,'USD',ACCESS_TOKEN)
        from_currency_id ,to_currency_id, rate , rate_date = convertion
        currency_data['from_currency_id'].append(from_currency_id)
        currency_data['to_currency_id'].append(to_currency_id)
        currency_data['rate'].append(rate)
        currency_data['rate_date'].append(rate_date)

    currency_convert_df = pd.DataFrame(currency_data)
    job_run_timestamp = datetime.now()
    currency_convert_df['job_run_timestamp'] = job_run_timestamp


    upload = input(f'Do you want to upload the currency convertion table to the database? (y/n) ')
    if upload == 'y':
        bigquery_client = get_bigquery_client()
        table_currency_convertion = "mercadolivrecase.currency_convertion"
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        job = bigquery_client.load_table_from_dataframe(currency_convert_df,
                                                        table_currency_convertion,
                                                         job_config=job_config)
        try:
            job.result()  # Espera o job terminar
            print(f"Data successfully uploaded to '{table_currency_convertion}'")
        except Exception as e:
            print(f"Error uploading data to '{table_currency_convertion}': {e}")

if __name__ == "__main__":
    main()