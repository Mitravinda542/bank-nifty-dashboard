# 📌 Imports
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

# 🎯 Bank Nifty tickers
bank_nifty_tickers = {
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Axis Bank": "AXISBANK.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "State Bank of India": "SBIN.NS",
    "IndusInd Bank": "INDUSINDBK.NS",
    "Bank of Baroda": "BANKBARODA.NS",
    "Punjab National Bank": "PNB.NS",
    "Canara Bank": "CANBK.NS",
    "Federal Bank": "FEDERALBNK.NS",
    "IDFC First Bank": "IDFCFIRSTB.NS",
    "AU Small Finance Bank": "AUBANK.NS"
}

# 📊 Fetch financial data
def fetch_data(tickers):
    data = []
    for name, symbol in tickers.items():
        stock = yf.Ticker(symbol)
        info = stock.info
        current = info.get("currentPrice", 0)
        high = info.get("fiftyTwoWeekHigh", 0)
        low = info.get("fiftyTwoWeekLow", 0)
        trend = "⬆️" if current > (high * 0.95) else ("⬇️" if current < (low * 1.05) else "↔️")
        data.append({
            "Company": name,
            "Current Price": current,
            "52-Week High": high,
            "52-Week Low": low,
            "Trend": trend,
            "Market Cap (Cr)": round(info.get("marketCap", 0) / 1e7, 2),
            "P/E Ratio": info.get("trailingPE", None),
            "ROE (%)": round(info.get("returnOnEquity", 0) * 100, 2)
        })
    return pd.DataFrame(data)

# 🎨 Stylize data
def style_df(df):
    return df.style\
        .highlight_max(subset=["Current Price", "ROE (%)"], color="lightgreen")\
        .highlight_min(subset=["P/E Ratio", "52-Week Low"], color="lightpink")\
        .format({
            "Current Price": "₹{:.2f}",
            "52-Week High": "₹{:.2f}",
            "52-Week Low": "₹{:.2f}",
            "Market Cap (Cr)": "{:.2f}",
            "P/E Ratio": "{:.2f}",
            "ROE (%)": "{:.2f}"
        })

# 📥 Excel export
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='BankNifty')
    return output.getvalue()

# ⚙️ Layout & Config
st.set_page_config(page_title="Bank Nifty Dashboard", layout="wide")
st.title("🏦 Bank Nifty Dashboard - Live Insights")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# 🛠️ Sidebar filters
st.sidebar.header("🧩 Dashboard Filters")
selected_companies = st.sidebar.multiselect("Choose companies to display", list(bank_nifty_tickers.keys()),
                                            default=list(bank_nifty_tickers.keys()))
min_roe = st.sidebar.slider("Minimum ROE (%)", 0, 30, 10)
max_pe = st.sidebar.slider("Maximum P/E Ratio", 5, 50, 25)

# 🧮 Main Data
filtered_tickers = {k: bank_nifty_tickers[k] for k in selected_companies}
df = fetch_data(filtered_tickers)
df = df[(df["ROE (%)"] >= min_roe) & (df["P/E Ratio"] <= max_pe)]

st.subheader("📋 Filtered Snapshot")
st.dataframe(style_df(df), use_container_width=True)

# 📊 Charting
st.subheader("📈 Price vs 52 Week High/Low")
for _, row in df.iterrows():
    fig, ax = plt.subplots()
    ax.bar(["Current", "High", "Low"],
           [row["Current Price"], row["52-Week High"], row["52-Week Low"]],
           color=["dodgerblue", "limegreen", "tomato"])
    ax.set_title(f"{row['Company']} {row['Trend']}")
    st.pyplot(fig)

# 📤 Download Excel
excel_data = convert_df_to_excel(df)
st.download_button("📥 Download Excel", excel_data, "bank_nifty_dashboard.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# 🧠 Tooltip Section
with st.expander("ℹ️ What These Metrics Mean"):
    st.markdown("""
- **Current Price**: Latest trading price.
- **52-Week High/Low**: Price range over the past 1 year.
- **Trend**: 
    - ⬆️ Near 52-week high
    - ⬇️ Near 52-week low
    - ↔️ In-between
- **ROE (%)**: Return on Equity—a measure of efficiency.
- **P/E Ratio**: Lower means potentially undervalued.
""")