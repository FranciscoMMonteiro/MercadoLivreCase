from dotenv import load_dotenv
import os
import json
from utils.token_functions import generate_new_tokens, update_env_token
from utils.api_fuctions import get_items
with open("site_ids.json", "r", encoding="utf-8") as f:
    site_ids = json.load(f)
from config import COUNTRY, PAGING_LIMIT,CONDITION
import pandas as pd
from datetime import datetime, timedelta
from database.database_connection import get_bigquery_client
from google.cloud import bigquery
import time


def main():
    load_dotenv('.env')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    with open("last_token_time.json", "r", encoding="utf-8") as last_token_file:
        last_token_time = json.load(last_token_file)["last_token_time"]

    bigquery_client = get_bigquery_client()
    query = """
        SELECT *
        FROM `mercadolivrecase.products`
    """

    df_products = bigquery_client.query(query).to_dataframe()

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

    data_item = {
        'item_id':[],
        'product_id':[],
        'product_name':[],
        'condition':[],
        'category_id':[],
        'seller_id':[],
        'price':[],
        'currency_id':[],
        'warranty':[],
        'shipping_mode':[]
    }

    for _,row in df_products.iterrows():
        stop = False
        offset = 0
        while stop == False:
            status_code,items = get_items(row['product_id'],CONDITION,offset,PAGING_LIMIT,ACCESS_TOKEN)
            if status_code not in [200,404]:
                print(f'Error getting items for product id {row["product_id"]} at offset {offset}. Status code: {status_code}.')
            elif status_code == 404:
                break
            if items['paging']['total'] == PAGING_LIMIT:
                offset += PAGING_LIMIT
            else:
                stop = True
            for item in items['results']:
                data_item['item_id'].append(item['item_id'])
                data_item['product_id'].append(row['product_id'])
                data_item['product_name'].append(row['product_name'])
                data_item['condition'].append(item['condition'])
                data_item['category_id'].append(item['category_id'])
                data_item['seller_id'].append(item['seller_id'])
                data_item['price'].append(item['price'])
                data_item['currency_id'].append(item['currency_id'])
                data_item['warranty'].append(item['warranty'])
                data_item['shipping_mode'].append(item['shipping']['mode'])
            time.sleep(0.3)

    df_item = pd.DataFrame(data_item)
    job_run_timestamp = datetime.now()
    df_item['job_run_timestamp'] = job_run_timestamp

    upload = 'y'
    #upload = input('Do you want to upload the item table to the database? (y/n) ')
    if upload == 'y':
        bigquery_client = get_bigquery_client()
        table_item = "mercadolivrecase.items"
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        job = bigquery_client.load_table_from_dataframe(df_item, table_item, job_config=job_config)
        try:
            job.result()  # Espera o job terminar
            print(f"Data successfully uploaded to '{table_item}'")
        except Exception as e:
            print(f"Error uploading data to '{table_item}': {e}")

if __name__ == "__main__":
    main()
