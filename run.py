import streamlit as st
from datetime import date

import pandas as pd

st.title ("Mining Profitability Chart")

st.sidebar.selectbox("Select GPU Type:", ("NVIDIA RX 3090", "NVIDIA RX 3080", "AMD RX 6800"))
st.sidebar.number_input("Number of GPUs", value=8, min_value=2, max_value=16, step=2)
st.sidebar.date_input("Start Date:", value=date(2021,1,1), min_value=date(2013,1,1), max_value=date.today())
st.sidebar.date_input("End Date:")
st.sidebar.text_input("Electricity Cost:", value="")
st.sidebar.text_input("Price Paid for Rigging:")

st.sidebar.selectbox("Strategy:", ("Mine & Hold", "Mine & Sell"))
st.sidebar.button("Sumbit")

df = pd.read_csv("./sample_data/eth_mining_results.csv")
df_c = df[['Mine & HODL','Mine & Sell', 'Buy ETH Directly']]

st.write("Returns of Mining/Accumulation Scenarios vs. Holding Ethereum")
st.line_chart(df_c)
