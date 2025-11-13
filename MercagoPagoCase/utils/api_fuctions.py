import json
import requests


def search_product_name(
    product_name: str,
    site_id: str,
    status_id: str,
    paging_limit: int,
    offset: int,
    access_token: str,
):
    
    url = f'https://api.mercadolibre.com/products/search?status={status_id}&site_id={site_id}&q={product_name}&offset={offset}&limit={paging_limit}'

    payload = {}
    headers = {
    'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)


def search_product_id(
    product_id: str,
    site_id: str,
    status_id: str,
    paging_limit: int,
    offset: int,
    access_token: str,
):
    
    url = f'https://api.mercadolibre.com/products/search?product_identifier={product_id}&status={status_id}&site_id={site_id}&offset={offset}&limit={paging_limit}'

    payload = {}
    headers = {
    'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)

def get_items(
    product_id: str,
    condition: str,
    offset: int,
    limit: int,
    access_token: str,
):
    
    url = (
        f'https://api.mercadolibre.com/products/{product_id}'+
        f'/items?offset={offset}&limit={limit}&condition={condition}'
    )

    payload = {}
    headers = {
    'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return (response.status_code,json.loads(response.text))

def get_sellers(
    seller_id_list: list,
    access_token: str,
):
    ids_string = ",".join(seller_id_list)

    url = (
        f'https://api.mercadolibre.com/users?ids={ids_string}'
    )

    payload = {}
    headers = {
    'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return (response.status_code,json.loads(response.text))

def get_items_sold(
    item_id_list: list,
    access_token: str,
):
    
    ids_string = ",".join(item_id_list)
    
    
    url = f"https://api.mercadolibre.com/items?ids={ids_string}"
    holder = '&attributes=id,title,sold_quantity'
    payload = {}
    headers = {
    'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return (response.status_code,json.loads(response.text))



def get_currency_convertion(   
    from_currency_id: str,
    to_currency_id: str,
    access_token: str,
):
    url = f'https://api.mercadolibre.com/currency_conversions/search?from={from_currency_id}&to={to_currency_id}'
    
    headers = {
    'Authorization': f'Bearer {access_token}',
    'x-format-new': 'true'
    }

    response = requests.request("GET", url, headers=headers)

    response_json = json.loads(response.text)

    return (response.status_code,(response_json['currency_base'],response_json['currency_quote'],response_json['rate'],response_json['creation_date']))