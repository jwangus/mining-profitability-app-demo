import re
from tokenize import String
import streamlit as st
from datetime import datetime, date, timedelta
from calculator import calc_matrix,calc

import pandas as pd

@st.cache
def calculate_matrix(today):
    return calc_matrix(st.secrets.KEEPA_API_KEY)

today = datetime.utcnow().date()
#st.write(f'today(UTC) : {today}')

c_df = calculate_matrix(today)
st.write(c_df)

min_date = c_df.index.min()
max_date = c_df.index.max()

gpu_selection:String = st.sidebar.selectbox("GPU Cards:", ("8 x NVIDIA GeForce RTX 3090", "8 x AMD Radeon RX 580"),
                                help="Select the number of GUPs and model that match your configuration.")

gpu_number_str, gpu_model = gpu_selection.split(" x ",2)
gpu_number = float(gpu_number_str)

#num_gpu = st.sidebar.number_input("Number of GPUs", value=8, min_value=4, max_value=16, step=4)
raw_start_date = st.sidebar.date_input("Mining Starts on:",
                                   value=date(2021,1,1), min_value=min_date, max_value=max_date, 
                                   help="Select a date in the past.")

raw_end_date = st.sidebar.date_input("Mining Ends on:",
                                   value=max_date, min_value=min_date, max_value=max_date, 
                                   help="Select a date in the past.")

len_in_days = (raw_end_date - raw_start_date).days + 1

electricity_cost_text = st.sidebar.text_input(
    "Electricity Cost:", value="10 cents per kWh")

#price_paid_text = st.sidebar.text_input(
#    "Non GPU Hardware Cost:", value="500",help="Cost of the rigging peripherals, e.g chassis")
#other_paid = st.sidebar.text_input("Other Cost Adjustment:", help="Put value in USD to reflect other initial investment in the mining rig.")

strategies = ("Mine & Hold", "Mine & Sell", "Mine & Sell 50%", "Buy BTC", "Buy ETH")

def show_results(df):
    r = calc(df, raw_start_date, raw_end_date, 0.24)
    r
    # results = f"""
    # ## Mining Profits from {raw_start_date} to {raw_end_date}
    # ### Length: {len_in_days} Days

    # ### Estimated Initial Investment (based on used GPU market price)
    # |  | Amount USD | Amount in ETH |
    # | --- | --- | --- |
    # | {gpu_selection} | {r[rig_price_start} | {rig_price_start_ether} |
 
    # ### Returns by Scenarios
    # | Scenarios | Return in USD | Return in ETH | % Return on Investment |
    # | --- | --- | --- | --- |
    # | {strategies[0]} | 2000 | 2.0 | 140% |
    # | {strategies[1]} | 2000 | 2.0 | 140% |
    # | {strategies[2]} | 2000 | 2.0 | 140% |
    # | {strategies[3]} | 2000 | 2.0 | 140% |
    # | {strategies[4]} | 2000 | 2.0 | 140% |

    # ### {strategies[0]}
    # | | Amount USD | Amount in ETH |
    # | --- | --- | --- |
    # | Ethereum | 6000 | 2.0 |
    # | USD | 0 | 0 |
    # | Rig Buyout | 3,800 | |
    # | __Total__ | 3,000 | |
    # | ROI | 150% | |

    # ### {strategies[1]}
    # | | Amount USD | Amount in ETH |
    # | --- | --- | --- |
    # | Ethereum | 6000 | 2.0 |
    # | USD | 0 | 0 |
    # | Rig Buyout | 3,800 | |
    # | __Total__ | 3,000 | |
    # | ROI | 150% | |

    # ### Returns Comparison Chart
    # """
    # st.markdown(results)
    # st.header("Historical Ether Price")
    # st.line_chart(rows_in_range ['ether_price'], width=800, use_container_width=False)
    # st.header("Daily Reward in Dollar per GH per Second")
    # st.line_chart(rows_in_range ['dollar_reward_per_ghps'], width=800, use_container_width=False)
    # st.header("Daily Reward in Ether per GH per Second")
    # st.line_chart(rows_in_range ['reward_per_ghps'], width=800, use_container_width=False)
    # st.header("Historical RX850 GPU price")
    # st.line_chart(rows_in_range ['gpu_price'], width=800, use_container_width=False)

if st.sidebar.button("Submit"):
    show_results(c_df)
else:
    st.error("Use the left panel to input your rigging info and click on Sumbit button to see results.")
