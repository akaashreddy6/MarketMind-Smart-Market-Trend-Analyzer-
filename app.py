# backend/app.py
# marketmind_app.py
import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="MarketMind", layout="wide")

st.title("📈 MarketMind – Smart Market Trend Analyzer")
st.write("Analyze market trends and get product recommendations")

# Simulated product database
PRODUCTS_DB = {
    "smartphone": [70, 75, 80, 85],
    "laptop": [60, 65, 63, 68],
    "headphones": [50, 55, 60, 70],
    "book": [20, 25, 30, 28],
    "shoes": [40, 45, 50, 55],
}

def calculate_trend(trend_history):
    last = trend_history[-1]
    prev = trend_history[-2]
    if last > prev:
        return "Trending 🔥", last
    elif last == prev:
        return "Stable ➖", last
    else:
        return "Falling ❄️", last

def predict_sales(score):
    growth = random.randint(-10, 20) + (score // 5)
    if growth > 15:
        return "Sales likely to increase 📈", "Invest"
    elif growth > 5:
        return "Sales might slightly increase ⬆️", "Hold"
    else:
        return "Sales might decrease 📉", "Avoid"

# --- Streamlit Input ---
product_input = st.text_input("Enter product name:", "").strip().lower()

if st.button("Analyze") and product_input:
    trend_history = PRODUCTS_DB.get(
        product_input,
        [random.randint(20, 50) for _ in range(4)]
    )

    trend, score = calculate_trend(trend_history)
    prediction, recommendation = predict_sales(score)

    # Display results
    st.subheader(f"Product: {product_input.title()}")
    st.write(f"**Trend:** {trend}")
    st.write(f"**Score:** {score}")
    st.write(f"**Prediction:** {prediction}")
    st.markdown(f"**Recommendation:** <span style='color: {'green' if recommendation=='Invest' else 'orange' if recommendation=='Hold' else 'red'}'>{recommendation}</span>", unsafe_allow_html=True)

    # Display trend chart
    df = pd.DataFrame({
        "Week": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "Trend Score": trend_history
    })
    st.line_chart(df.set_index("Week"))
