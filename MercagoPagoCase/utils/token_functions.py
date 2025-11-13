import json
import requests
import os

def generate_new_tokens(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN):
    url = 'https://api.mercadolibre.com/oauth/token'

    payload = f'grant_type=refresh_token&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={REFRESH_TOKEN}'
    headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        print('New tokens obtained successfully.')
        response_json = json.loads(response.text)
        return (response_json['access_token'],response_json['refresh_token'])
    else:
        raise ValueError(f'Failed to obtain new tokens. Status code: {response.status_code}')


def update_env_token(key ,new_token, env_path='.env'):
    """Atualiza ou cria uma variável no arquivo .env"""
    lines = []
    found = False

    # Lê o .env atual, se existir
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(f'{key}'):
                    lines.append(f'{key} = "{new_token}"\n')
                    found = True
                else:
                    lines.append(line)
    
    # Se a variável não existia, adiciona no final
    if not found:
        lines.append(f'{key}]={new_token}\n')

    # Reescreve o arquivo
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)