from unittest import result
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

def _get_gpu_prices_from_keepa (product_id, api_key):
    def clean_up(raw_df):
        # clean up the data to make it look like other time series
        raw_df['Date(UTC)'] = pd.to_datetime(raw_df.index).date
        raw_df.dropna(inplace=True)
        clean_series = raw_df.groupby(['Date(UTC)'])['value'].mean()
        clean_df = clean_series.reset_index()
        clean_df.set_index('Date(UTC)',inplace=True)
        return clean_df

    api = keepa.Keepa(api_key)
    #products = api.query('B06XZQMMHJ')
    products = api.query(product_id)
    df_new = clean_up(pd.DataFrame(products[0]['data']['df_NEW']))
    df_new.rename(columns={'value':'new_gpu_price'},inplace=True)

    df_used = clean_up(pd.DataFrame(products[0]['data']['df_USED']))
    df_used.rename(columns={'value':'used_gpu_price'},inplace=True)

    return df_new, df_used
 
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

    new_df, up_df = _get_gpu_prices_from_keepa ('B06XZQMMHJ', keepa_api_key)
    df = df.merge(new_df, left_index=True, right_index=True, how='left')
    df = df.merge(up_df, left_index=True, right_index=True, how='left')

    return df

def _add_calculated_cols (df):
    # daily reward per GH/s(ghps) of hash rate 
    df['reward_per_ghps'] = df['block_reward'] / df['hash_rate']
    # convert to dollar
    df['dollar_reward_per_ghps'] = df['reward_per_ghps'] * df['ether_price']
    #fill the gaps in gpu price
    df['used_gpu_price'].interpolate(inplace=True)
    df['used_gpu_price'].fillna(method='backfill', inplace=True)
    df['new_gpu_price'].interpolate(inplace=True)
    df['new_gpu_price'].fillna(method='backfill', inplace=True)

def calc_matrix(keepa_api_key):
    ''' A matrix with enough data for calculation
    '''
    df = _prepare_calc_data(keepa_api_key)
    _add_calculated_cols(df)
    return df

def calc (df, start_date, end_date, gpu_giga_hashrate, rig_price=None, electricity_price=0.1, gpu_number=8, 
chassis_cost=500, rig_kilowatt=1, buyback_multiplier=1):
    '''
     Returns calculation results
        Parameters:
            df (DataFrame): A DF object with historical data populated.
            start_date (datetime): Mining starts on this date
            end_date (datetime): Ming ends on this date
            gpu_giga_hashrate: capable of performing number of hashes per hour.
            gpu_number: number of GPU boards.
            rig_price (float): The price of the rig.
            electricity_price: In dollar killo Wattes per hour.
            chassis_cost (float): The cost of the chassis that hosts the GPU cards
            rig_kilowatt (float): The power consumption in Kilowatt 
            buyback_multiplier: This multiplier will be applied to calculated buyback price based on used GPU card price.
        Returns:
            calulation results.
            
            Here is an example:
            "rig_price":2958.248888888889
            "rig_buyback_price":5100
            "start_ether_price":730.6
            "end_ether_price":2541.6
            "ether_mined":2.214013075929777
            "ether_mined_dollar":5574.053511512345
            "start_date":"datetime.date(2021, 1, 1)"
            "end_date":"datetime.date(2022, 1, 23)"
            "electricity_price":0.1
            "total_electricity_cost":931.2
            "rows_in_range": dataframe only contains the rows between the start date and end date.  Can
                             be used for creating charts.
    '''
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    num_hours = (end - start).total_seconds()//3600 + 24

    start_ether_price = df.at[start, "ether_price"]
    end_ether_price = df.at[end, "ether_price"]

    if not rig_price:
        rig_price = gpu_number * df.at[start, "new_gpu_price"] + chassis_cost

    total_electricity_cost = electricity_price * num_hours * rig_kilowatt
    rows_in_range = df.loc[(df.index >= start) & (df.index <= end)]
    ether_mined_dollar = rows_in_range['dollar_reward_per_ghps'].sum()*gpu_giga_hashrate
    ether_mined = rows_in_range['reward_per_ghps'].sum()*gpu_giga_hashrate

    rig_buyback_price = (gpu_number * df.at[end, "used_gpu_price"] + chassis_cost)*buyback_multiplier

    expense = rig_price + total_electricity_cost

    results = {
        "rig_price" : rig_price,
        "rig_buyback_price" : rig_buyback_price,
        "start_ether_price" : start_ether_price,
        "end_ether_price" : end_ether_price,
        "hold_100_ether_acct" : ether_mined,
        "hold_100_ether_acct_usd_value" : ether_mined * end_ether_price,
        "hold_100_usd_acct_usd_value" : 0,
        "hold_0_ether_acct_usd_value" : 0,
        "hold_0_usd_acct_usd_value" : ether_mined_dollar,
        "hold_50_ether_acct_usd_value" : ether_mined * end_ether_price / 2,
        "hold_50_usd_acct_usd_value" :  ether_mined_dollar / 2,
        "start_date" : start.date(),
        "end_date" : end.date(),
        "electricity_price" : electricity_price,
        "total_electricity_cost" : total_electricity_cost,
        "rows_in_range" : rows_in_range
    }

    results["total_investment"] = expense
    results["hold_100_pnl"] = rig_buyback_price + results["hold_100_ether_acct_usd_value"] + results["hold_100_usd_acct_usd_value"] - expense
    results["hold_50_pnl"] = rig_buyback_price + results["hold_50_ether_acct_usd_value"] + results["hold_50_usd_acct_usd_value"] - expense
    results["hold_0_pnl"] = rig_buyback_price + results["hold_0_ether_acct_usd_value"] + results["hold_0_usd_acct_usd_value"] - expense
    results["buy_ether_ether_acct_value"] = results["total_investment"]/start_ether_price
    results["buy_ether_ether_acct_usd_value"] = results["buy_ether_ether_acct_value"] * end_ether_price
    results["buy_ether_usd_acct_usd_value"] = 0
    results["buy_ether_pnl"] = results["buy_ether_ether_acct_usd_value"] - results["total_investment"]
    return results
