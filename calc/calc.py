from datetime import date, timedelta
from venv import create
import pandas as pd
import numpy as np

data_file_info = {
    'hashrate', 'blockreward', 'gasused', 'etherprice', 'gpu_price' 
}

def create_blank_working_df ():
    # 1. Create a list of dates.  It will be used as the index of our dataframe
    one_day = timedelta(days=1)
    end_range = date.today()
    number_days = 5
    d_list = [date.today() - timedelta(days=i) for i in range(number_days)]
    # 2. Create a blank dataframe with index of dates.
    return pd.DataFrame (index=pd.to_datetime(d_list))

def add_data (working_df, data_file_name):
    df_merge = pd.read_csv(f'../sample_data/{data_file_name}.csv', 
                          index_col='Date(UTC)', 
                          converters = {'Date(UTC)': pd.to_datetime},
                          usecols = [ 'Date(UTC)', 'Value']
                         )
    df_merge.rename (columns={'Value': data_file_name}, inplace=True)
    return working_df.merge(df_merge, left_index=True, right_index=True, how='left')

def create_working_df():
    working_df = create_blank_working_df()
    for data_file_name in data_file_info:
        working_df = add_data(working_df, data_file_name)

    return working_df

if __name__ == '__main__':
    print (create_working_df())