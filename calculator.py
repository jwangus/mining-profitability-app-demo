import pandas as pd
import requests
from io import BytesIO
import keepa
from datetime import date, timedelta, datetime

def _get_from_etherscan (data_type):
    '''
    data_type example:  hashrate, blockreward
    '''
    response = requests.get(f'https://etherscan.io/chart/{data_type}?output=csv',
                       headers = {'user-agent':'Mozilla/5.0'})
    response.status_code
    
    if (response.status_code != 200):
        return

    df = pd.read_csv(BytesIO(response.content),
                 index_col='Date(UTC)', 
                 converters = {'Date(UTC)': pd.to_datetime},
                 usecols = [ 'Date(UTC)', 'Value'])

    return df

def _get_used_price_from_keepa (product_id, api_key):
    api = keepa.Keepa(api_key)
    #products = api.query('B06XZQMMHJ')
    products = api.query(product_id)
    df = pd.DataFrame(products[0]['data']['df_USED'])
    
    df['Date(UTC)'] = pd.to_datetime(df.index).date

    # clean up the data to make it look like other time series
    df.dropna(inplace=True)
    clean_series = df.groupby(['Date(UTC)'])['value'].mean()
    clean_df = clean_series.reset_index()
    clean_df.set_index('Date(UTC)',inplace=True)
    clean_df.rename(columns={'value':'Value'},inplace=True)

    return clean_df
 
def _create_blank_df ():
    number_days = 1500
    d_list = [datetime.utcnow().date() - timedelta(days=i) for i in range(1, number_days+1)]
    return pd.DataFrame (index=pd.to_datetime(d_list))

def _prepare_calc_data(keepa_api_key):
    df = _create_blank_df()

    hr_df = hr = _get_from_etherscan('hashrate')
    hr_df.rename (columns={'Value': 'hash_rate'}, inplace=True)
    df = df.merge(hr_df, left_index=True, right_index=True, how='left')

    br_df = _get_from_etherscan('blockreward')
    br_df.rename (columns={'Value': 'block_reward'}, inplace=True)
    df = df.merge(br_df, left_index=True, right_index=True, how='left')

    ep_df = _get_from_etherscan('etherprice')
    ep_df.rename (columns={'Value': 'ether_price'}, inplace=True)
    df = df.merge(ep_df, left_index=True, right_index=True, how='left')

    up_df = _get_used_price_from_keepa ('B06XZQMMHJ', keepa_api_key)
    up_df.rename (columns={'Value': 'gpu_price'}, inplace=True)
    df = df.merge(up_df, left_index=True, right_index=True, how='left')

    return df

def _add_calculated_cols (df):
    # daily reward per GH/s(ghps) of hash rate 
    df['reward_per_ghps'] = df['block_reward'] / df['hash_rate']
    # convert to dollar
    df['dollar_reward_per_ghps'] = df['reward_per_ghps'] * df['ether_price']
    #fill the gaps in gpu price
    df['gpu_price'].interpolate(inplace=True)
    df['gpu_price'].fillna(method='backfill', inplace=True)
    
def calc_matrix(keepa_api_key):
    ''' A matrix with enough data for calculation
    '''
    df = _prepare_calc_data(keepa_api_key)
    _add_calculated_cols(df)
    return df
