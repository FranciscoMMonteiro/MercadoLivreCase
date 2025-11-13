from dotenv import load_dotenv
import os
import json
from utils.token_functions import generate_new_tokens, update_env_token
from utils.api_fuctions import get_sellers
with open("site_ids.json", "r", encoding="utf-8") as f:
    site_ids = json.load(f)
import pandas as pd
from datetime import datetime
from database.database_connection import get_bigquery_client
from google.cloud import bigquery
import time

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

    bigquery_client = get_bigquery_client()
    query = """
        SELECT *
        FROM `mercadolivrecase.items`
    """

    df_items = bigquery_client.query(query).to_dataframe()
    sellet_ids_list = list(df_items['seller_id'].astype(str).unique())


    data_seller = {
    'seller_id':[],
    'nickname':[],
    'country_id':[],
    'address':[],
    'user_type':[],
    'site_id':[],
    'transactions':[],
    'transactions_period':[],
    'site_status':[],
    }

    step_i = 10
    for i in range(0,len(sellet_ids_list),step_i):
        status_code_seller, sellers = get_sellers(sellet_ids_list[i:i+step_i],ACCESS_TOKEN)
        if status_code_seller not in [200,404]:
            print(f'Error getting items for sellers id {sellet_ids_list[i:i+step_i]}. Status code: {status_code_seller}.')
        elif status_code_seller == 404:
            continue
        for seller in sellers:
            s = seller['body']
            data_seller['seller_id'].append(s['id'])
            data_seller['nickname'].append(s['nickname'])
            data_seller['country_id'].append(s['country_id'])
            data_seller['address'].append(str(s['address']['city']+", "+s['address']['state']))
            data_seller['user_type'].append(s['user_type'])
            data_seller['site_id'].append(s['site_id'])
            data_seller['transactions'].append(s['seller_reputation']['transactions']['total'])
            data_seller['transactions_period'].append(s['seller_reputation']['transactions']['period'])
            data_seller['site_status'].append(s['status']['site_status'])
        time.sleep(0.3)
    
    df_sellers = pd.DataFrame(data_seller)
    job_run_timestamp = datetime.now()
    df_sellers['job_run_timestamp'] = job_run_timestamp

    upload = input('Do you want to upload the seller table to the database? (y/n) ')
    if upload == 'y':
        bigquery_client = get_bigquery_client()
        table_seller = "mercadolivrecase.sellers"
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        job = bigquery_client.load_table_from_dataframe(df_sellers, table_seller, job_config=job_config)
        try:
            job.result()  # Espera o job terminar
            print(f"Data successfully uploaded to '{table_seller}'")
        except Exception as e:
            print(f"Error uploading data to '{table_seller}': {e}")

if __name__ == "__main__":
    main()