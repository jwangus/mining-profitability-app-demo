import pandas as pd
import requests
import keepa

from _secret import KEEPA_API_KEY

# file name is the key, URL is the value
URL_info = {
    'hashrate' : 'https://etherscan.io/chart/hashrate?output=csv',
    'blockreward' : 'https://etherscan.io/chart/blockreward?output=csv',
    'gasused' : 'https://etherscan.io/chart/gasused?output=csv',
    'etherprice' : 'https://etherscan.io/chart/etherprice?output=csv'
}

def download(file_name):
    headers = {'user-agent':'Mozilla/5.0'}
    r = requests.get(URL_info[file_name], headers = headers)
    if r.status_code != 200:
        return
    with open(f'../sample_data/{file_name}.csv', 'wb') as f:
        f.write(r.content)

def download_gpu_price():
    api = keepa.Keepa(KEEPA_API_KEY)
    products = api.query('B06XZQMMHJ')
    df = pd.DataFrame(products[0]['data']['df_USED'])
    df.to_csv('../sample_data/gpu_price.csv')


def download_all():
    for file_name in URL_info:
        download(file_name)
    download_gpu_price()

if __name__ == "__main__":
    download_all()
