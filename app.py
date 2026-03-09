
import streamlit as st
import random
import pandas as pd
import json
import os
import hashlib
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="MarketMind AI", layout="wide")

# --- Users File ---
USERS_FILE = "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {"admin": hash_password("12345")}

def save_users(users_dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users_dict, f)

# --- Session State ---
if "users" not in st.session_state:
    st.session_state.users = load_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "signup"

# --- Product Database ---
PRODUCTS_DB = {
    "smartphone": [70, 75, 80, 85],
    "laptop": [60, 65, 63, 68],
    "headphones": [50, 55, 60, 70],
    "book": [20, 25, 30, 28],
    "shoes": [40, 45, 50, 55],
    "tablet": [65, 70, 72, 78],
    "smartwatch": [55, 60, 64, 69],
    "camera": [50, 52, 55, 60],
    "gaming console": [75, 78, 82, 90]
}

# --- AI Prediction ---
def predict_next_trend(history):

    X = np.array(range(len(history))).reshape(-1,1)
    y = np.array(history)

    model = LinearRegression()
    model.fit(X,y)

    next_day = np.array([[len(history)]])
    prediction = model.predict(next_day)

    return round(prediction[0],2)

# --- Trend Status ---
def calculate_trend(trend_history):

    last = trend_history[-1]
    prev = trend_history[-2]

    if last > prev:
        return "Trending 🔥", last
    elif last == prev:
        return "Stable ➖", last
    else:
        return "Falling ❄️", last

# --- Recommendation ---
def recommendation(score):

    if score > 80:
        return "Invest 📈"
    elif score > 60:
        return "Hold ⏳"
    else:
        return "Avoid ⚠️"

# --- Signup Page ---
def signup_page():

    st.title("📝 MarketMind AI - Sign Up")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):

        if username in st.session_state.users:
            st.error("Username exists")

        else:
            st.session_state.users[username] = hash_password(password)
            save_users(st.session_state.users)

            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "dashboard"

# --- Login Page ---
def login_page():

    st.title("🤖 MarketMind AI Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if st.session_state.users.get(username) == hash_password(password):

            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "dashboard"

        else:
            st.error("Invalid login")

    if st.button("Create Account"):
        st.session_state.page = "signup"

# --- Dashboard ---
def dashboard_page():

    st.sidebar.write("Logged in as:", st.session_state.username)

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"

    st.title("📊 MarketMind AI Dashboard")

    st.sidebar.write("### Products")

    for p in PRODUCTS_DB:
        st.sidebar.write(p)

    st.divider()

    # --- Top Trending ---
    st.subheader("🔥 Top Trending Products")

    trending = sorted(PRODUCTS_DB.items(), key=lambda x: x[1][-1], reverse=True)

    for p in trending[:3]:
        st.write(p[0].title(), "Score:", p[1][-1])

    st.divider()

    product = st.text_input("Enter product")

    if st.button("Analyze"):

        product = product.lower()

        trend_history = PRODUCTS_DB.get(product, [random.randint(30,60) for _ in range(4)])

        trend, score = calculate_trend(trend_history)

        ai_prediction = predict_next_trend(trend_history)

        rec = recommendation(score)

        st.subheader(product.title())

        st.write("Trend:", trend)
        st.write("Current Score:", score)

        st.write("🤖 AI Next Trend Prediction:", ai_prediction)

        st.write("Recommendation:", rec)

        dates = pd.date_range(end=pd.Timestamp.today(), periods=4)

        df = pd.DataFrame({
            "Date":dates,
            "Trend":trend_history
        })

        df = df.set_index("Date")

        st.line_chart(df)

        st.dataframe(df)

        csv = df.to_csv().encode()

        st.download_button(
            "Download Report",
            csv,
            "trend_report.csv",
            "text/csv"
        )

    # --- Product Comparison ---
    st.divider()

    st.subheader("⚔️ Compare Products")

    p1 = st.selectbox("Product 1", list(PRODUCTS_DB.keys()))
    p2 = st.selectbox("Product 2", list(PRODUCTS_DB.keys()), index=1)

    if st.button("Compare"):

        df = pd.DataFrame({
            p1:PRODUCTS_DB[p1],
            p2:PRODUCTS_DB[p2]
        })

        st.line_chart(df)

# --- Main App ---
if st.session_state.page == "signup":
    signup_page()

elif st.session_state.page == "login":
    login_page()

elif st.session_state.page == "dashboard":

    if st.session_state.logged_in:
        dashboard_page()

    else:
        st.session_state.page = "login"
