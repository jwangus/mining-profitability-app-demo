import pandas as pd
import requests
import keepa

from _secret import KEEPA_API_KEY

# file name is the key, URL is the value
data_file_info = {
    'hashrate' : 'https://etherscan.io/chart/hashrate?output=csv',
    'blockreward' : 'https://etherscan.io/chart/blockreward?output=csv',
    'gasused' : 'https://etherscan.io/chart/gasused?output=csv',
    'etherprice' : 'https://etherscan.io/chart/etherprice?output=csv'
}

def download(file_name):
    headers = {'user-agent':'Mozilla/5.0'}
    r = requests.get(data_file_info[file_name], headers = headers)
    if r.status_code != 200:
        return
    with open(f'../sample_data/{file_name}.csv', 'wb') as f:
        f.write(r.content)

def download_gpu_price():
    api = keepa.Keepa(KEEPA_API_KEY)
    products = api.query('B06XZQMMHJ')
    df = pd.DataFrame(products[0]['data']['df_USED'])
    df.to_csv('../sample_data/gpu_price_raw.csv')

def convert_gpu_price():
    df = pd.read_csv('../sample_data/gpu_price_raw.csv', index_col=0, )
    df['Date(UTC)'] = pd.to_datetime(df.index).date

    # clean up the data to make it look like other time series
    df.dropna(inplace=True)
    clean_series = df.groupby(['Date(UTC)'])['value'].mean()
    clean_df = clean_series.reset_index()
    clean_df.set_index('Date(UTC)',inplace=True)
    clean_df.rename(columns={'value':'Value'},inplace=True)
    clean_df.to_csv('../sample_data/gpu_price.csv')


def download_all():
    for file_name in data_file_info:
        download(file_name)
    download_gpu_price()
    convert_gpu_price()

if __name__ == "__main__":
    #download_all()
    convert_gpu_price()
