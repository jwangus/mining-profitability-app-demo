import streamlit as st
from datetime import date

import pandas as pd

st.title("Historical Mining Profits Calculator")

gpu_type = st.sidebar.selectbox("GPU Cards:", ("8 x NVIDIA GeForce RTX 3090", "8 x AMD Radeon RX 580"),
                                help="Select the number of GUPs and model that match your configuration.")

#num_gpu = st.sidebar.number_input("Number of GPUs", value=8, min_value=4, max_value=16, step=4)
start_date = st.sidebar.date_input("Mining Starts on:",
                                   value=date(2021, 1, 1), min_value=date(2013, 1, 1), max_value=date.today(), 
                                   help="Select a date in the past.")

len_in_days = st.sidebar.number_input(
    "Number of Days of Mining:", value=360, min_value=0, max_value=1080, step = 30)

electricity_cost = st.sidebar.text_input(
    "Electricity Cost:", value="10 cents per KW")

price_paid = st.sidebar.text_input(
    "Non GPU Harware Cost:", help="Cost of the rigging peripherals, e.g chassis")
other_paid = st.sidebar.text_input("Other Cost Adjustment:", help="Put value in USD to reflect other initial investment in the mining rig.")

strategy = st.sidebar.selectbox("Strategy:", ("Mine & Hold", "Mine & Sell"))

if st.sidebar.button("Sumbit"):
    df = pd.read_csv("./sample_data/eth_mining_results.csv")
    df_c = df[['Mine & HODL', 'Mine & Sell', 'Buy ETH Directly']]
    st.write("Returns of Mining/Accumulation Scenarios vs. Holding Ethereum")
    st.line_chart(df_c)
else:
    st.error("Use the left panel to input your rigging info and click on Sumbit button to see results.")
