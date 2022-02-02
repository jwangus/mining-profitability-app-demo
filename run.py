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
# st.write(c_df)

min_date = c_df.index.min()
max_date = c_df.index.max()

#gpu_selection:str = st.sidebar.selectbox("GPU Cards:", ("8 x NVIDIA GeForce RTX 3090", "8 x AMD Radeon RX 580"),
#                                help="Select the number of GUPs and model that match your configuration.")

gpu_selection:str = st.sidebar.selectbox("GPU Cards:", ("8 x AMD Radeon RX 580 8GB", ""),
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

electricity_cost_cents = st.sidebar.number_input(
    "Electricity Cost (cents per Kwh):", value=10, min_value=0, max_value=100)

strategies = ("Mine & Hold", "Mine & Sell", "Mine & Sell 50%", "Buy BTC", "Buy ETH")

def show_results(df):
    r = calc(df, raw_start_date, raw_end_date, 0.24, rig_kilowatt=0.13*8, 
        electricity_price = electricity_cost_cents/100.0)
    rows_in_range = r['rows_in_range']
    results = f"""
    ## Ethereum Mining Profit and Loss Calculator
    ### Market value changes in {len_in_days} days ending on {raw_end_date}
    |                  |  USD Value on {raw_start_date}  |  USD Value on {raw_end_date}  | Change |
    |------------------|:-------------------------------:|:-----------------------------:|:------:|
    | Ether Price      |  $ {r['start_ether_price']:,.0f} | $ {r['end_ether_price']:,.0f} | $ {(r['end_ether_price'] - r['start_ether_price']):,.2f} |
    | Estimated Rig Value |  $ {r['rig_price']:,.0f} | $ {r['rig_buyback_price']:,.0f} | $ {(r['rig_buyback_price'] - r['rig_price']):,.2f} |


    ### Returns on totoal investment of $ {r["total_investment"]:,.0f}
    |                      | Mine & Hold   | Mine & Hold 50% | Mine & Sell      | Buy Ether  |
    |----------------------|:-------------:|:---------------:|:----------------:|:---------:|
    | Rig Buyback Value    | $ {r['rig_buyback_price']:,.0f} | $ {r['rig_buyback_price']:,.0f} | $ {r['rig_buyback_price']:,.0f} | - |
    | Ether Account Value  | $ {r['hold_100_ether_acct_usd_value']:,.0f} | $ {r['hold_50_ether_acct_usd_value']:,.0f} | - | $ {r["buy_ether_ether_acct_usd_value"]:,.0f} | 
    | USD Account Value    | - | $ {r['hold_50_usd_acct_usd_value']:,.0f} | $ {r['hold_0_usd_acct_usd_value']:,.0f} | - |
    | Rig Purchase Expense | $ {r['rig_price']:,.0f} | $ {r['rig_price']:,.0f} | $ {r['rig_price']:,.0f} | - |
    | Electricity Expense  | $ {r['total_electricity_cost']:,.0f} | $ {r['total_electricity_cost']:,.0f} | $ {r['total_electricity_cost']:,.0f} | - |
    | Total Expense/Investment | $ {r["total_investment"]:,.0f} | $ {r["total_investment"]:,.0f} | $ {r["total_investment"]:,.0f}| $ {r["total_investment"]:,.0f} |
    | PnL                  | $ {r['hold_100_pnl']:,.0f} | $ {r['hold_50_pnl']:,.0f} | $ {r['hold_0_pnl']:,.0f} | $ {r["buy_ether_pnl"]:,.0f} |

    """
    st.markdown(results)
    st.write("### Historical Ethereum Price")
    st.line_chart(rows_in_range ['ether_price'], width=800, use_container_width=False)
    st.write("### Daily Reward in Dollar per GH per Second")
    st.line_chart(rows_in_range ['dollar_reward_per_ghps'], width=800, use_container_width=False)
    st.write("### Daily Reward in Ether per GH per Second")
    st.line_chart(rows_in_range ['reward_per_ghps'], width=800, use_container_width=False)
    st.write("### Historical AMD RX 580 8GB GPU Card Prices")
    st.line_chart(rows_in_range [['new_gpu_price','used_gpu_price']], width=800, use_container_width=False)

if st.sidebar.button("Submit"):
    show_results(c_df)
else:
    st.error("Use the left panel to input your rigging info and click on Sumbit button to see results.")
