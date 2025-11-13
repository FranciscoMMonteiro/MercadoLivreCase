from dotenv import load_dotenv
import os
import json
from utils.token_functions import generate_new_tokens, update_env_token
from utils.api_fuctions import search_product_name
with open("site_ids.json", "r", encoding="utf-8") as f:
    site_ids = json.load(f)
from config import COUNTRY, STATUS_ID, PAGING_LIMIT, PRODUCT_NAME
import pandas as pd
from datetime import datetime, timedelta
from database.database_connection import get_bigquery_client
from google.cloud import bigquery



def main():
    load_dotenv('.env')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    with open("last_token_time.json", "r", encoding="utf-8") as last_token_file:
        last_token_time = json.load(last_token_file)["last_token_time"]


    if datetime.now() - datetime.fromisoformat(last_token_time) > timedelta(hours=4):
        #get_new_token = input('Do you want to get a new refresh token? (y/n): ')
        get_new_token = True
    else:
        get_new_token = False
        
    if get_new_token:
        new_access_token, new_refresh_token = generate_new_tokens(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
        update_env_token('ACCESS_TOKEN',new_access_token)
        update_env_token('REFRESH_TOKEN',new_refresh_token)
        ACCESS_TOKEN = new_access_token
        REFRESH_TOKEN = new_refresh_token
        last_token_time = datetime.now().isoformat()
        with open("last_token_time.json", "w", encoding="utf-8") as f:
            f.write('{"last_token_time" :'+ '"' + last_token_time+'"}')

    site_id = site_ids[COUNTRY]

    data_search_by_name = {
    'product_id':[],
    'product_name':[]
    }

    # Samsung Galaxy S25
    #product_name = input('Enter the product name to be search (Default="Samsung Galaxy S25"): ') or  'Samsung Galaxy S25'
    print(f"Searching for {PRODUCT_NAME}")
    product_name_lower = str.lower(PRODUCT_NAME)
    for offset in range(0,201,PAGING_LIMIT):
        response_json = search_product_name(PRODUCT_NAME,site_id,
                                            STATUS_ID,PAGING_LIMIT,
                                            offset,ACCESS_TOKEN)
        for item in response_json['results']:
            if product_name_lower in str.lower(item['name']):
                data_search_by_name['product_id'].append(item['id'])
                data_search_by_name['product_name'].append(item['name'])

    df_search = pd.DataFrame(data_search_by_name)
    job_run_timestamp = datetime.now()
    df_search['job_run_timestamp'] = job_run_timestamp


    upload = 'y'
    #upload = input('Do you want to upload the product table to the database? (y/n) ')
    if upload == 'y':
        bigquery_client = get_bigquery_client()
        table_product = "mercadolivrecase.products"
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        job = bigquery_client.load_table_from_dataframe(df_search, table_product, job_config=job_config)
        try:
            job.result()  # Espera o job terminar
            print(f"Data successfully uploaded to '{table_product}'")
        except Exception as e:
            print(f"Error uploading data to '{table_product}': {e}")

if __name__ == "__main__":
    main()
