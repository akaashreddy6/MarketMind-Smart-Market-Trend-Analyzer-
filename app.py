import streamlit as st
import pandas as pd
import numpy as np
import random

st.set_page_config(page_title="MarketMind AI", layout="wide")

# ---------- Product Database ----------
PRODUCTS_DB = {
    "smartphone":[70,75,80,85],
    "laptop":[60,65,63,68],
    "headphones":[50,55,60,70],
    "shoes":[40,45,50,55],
    "tablet":[65,70,72,78],
    "smartwatch":[55,60,64,69],
    "camera":[50,52,55,60],
    "gaming console":[75,78,82,90]
}

# ---------- Simple AI Prediction ----------
def predict_future(history, days=3):

    x = np.arange(len(history))
    y = np.array(history)

    slope, intercept = np.polyfit(x, y, 1)

    predictions = []

    for i in range(1, days+1):
        next_value = slope*(len(history)+i-1) + intercept
        predictions.append(round(next_value,2))

    return predictions

# ---------- Demand Score ----------
def demand_score(score):

    if score > 80:
        return "Very High 🔥"
    elif score > 65:
        return "High 📈"
    elif score > 50:
        return "Medium ➖"
    else:
        return "Low 📉"

# ---------- Sidebar ----------
st.sidebar.title("📊 MarketMind AI")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard","Product Analysis","Product Comparison","Top Trends"]
)

# ---------- Dashboard ----------
if menu == "Dashboard":

    st.title("📊 MarketMind AI Dashboard")

    total_products = len(PRODUCTS_DB)

    avg_score = int(np.mean([v[-1] for v in PRODUCTS_DB.values()]))

    top_product = max(PRODUCTS_DB, key=lambda x: PRODUCTS_DB[x][-1])

    col1,col2,col3 = st.columns(3)

    col1.metric("Products Tracked", total_products)
    col2.metric("Average Trend Score", avg_score)
    col3.metric("Top Product", top_product.title())

# ---------- Product Analysis ----------
elif menu == "Product Analysis":

    st.header("🔍 Product Trend Analysis")

    product = st.selectbox("Select Product", list(PRODUCTS_DB.keys()))

    history = PRODUCTS_DB[product]

    score = history[-1]

    future = predict_future(history)

    demand = demand_score(score)

    col1,col2,col3 = st.columns(3)

    col1.metric("Current Score", score)
    col2.metric("Next Day Prediction", future[0])
    col3.metric("Demand Level", demand)

    st.subheader("Trend History")

    dates = pd.date_range(end=pd.Timestamp.today(), periods=len(history))

    df = pd.DataFrame({
        "Date":dates,
        "Trend":history
    }).set_index("Date")

    st.line_chart(df)

    st.subheader("AI Forecast")

    forecast_df = pd.DataFrame({
        "Day":[1,2,3],
        "Predicted Score":future
    })

    st.bar_chart(forecast_df.set_index("Day"))

    st.dataframe(df)

    csv = df.to_csv().encode()

    st.download_button(
        "Download Report",
        csv,
        "marketmind_report.csv",
        "text/csv"
    )

# ---------- Product Comparison ----------
elif menu == "Product Comparison":

    st.header("⚔️ Compare Products")

    p1 = st.selectbox("Product 1", list(PRODUCTS_DB.keys()))
    p2 = st.selectbox("Product 2", list(PRODUCTS_DB.keys()), index=1)

    df = pd.DataFrame({
        p1:PRODUCTS_DB[p1],
        p2:PRODUCTS_DB[p2]
    })

    st.line_chart(df)

# ---------- Top Trends ----------
elif menu == "Top Trends":

    st.header("🔥 Top Trending Products")

    ranking = sorted(PRODUCTS_DB.items(), key=lambda x:x[1][-1], reverse=True)

    for i,(p,data) in enumerate(ranking):

        st.write(f"{i+1}. **{p.title()}** — Score: {data[-1]}")


