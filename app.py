
import streamlit as st
import random
import pandas as pd
import json
import os

# --- Page Config ---
st.set_page_config(page_title="MarketMind", layout="wide")

# --- Users File for Persistent Storage ---
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {"admin": "12345"}

def save_users(users_dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users_dict, f)

# --- Initialize session state ---
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
}

# --- Helper Functions ---
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

def trend_overview(trend_history, product_name):
    """
    Generate a short description based on trend history.
    """
    if len(trend_history) < 2:
        return "Not enough data to determine trend."

    last = trend_history[-1]
    prev = trend_history[-2]
    avg = sum(trend_history) / len(trend_history)

    description = f"The latest trend score for **{product_name.title()}** is {last}. "

    if last > prev and last > avg:
        description += "The product is showing a strong upward trend 📈. It may be a good investment opportunity."
    elif last > prev and last <= avg:
        description += "The product is trending upward slightly ⬆️. Monitor its performance for potential growth."
    elif last == prev:
        description += "The product trend is stable ➖. Demand is consistent."
    else:
        description += "The product is showing a downward trend 📉. Consider caution before investing."

    return description

# --- Sign-Up Page ---
def signup_page():
    st.title("📝 Sign Up for MarketMind")
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/87/Logo_sample.png", width=150)

    username = st.text_input("Choose a username", key="signup_user")
    password = st.text_input("Choose a password", type="password", key="signup_pass")
    
    if st.button("Sign Up", key="signup_btn"):
        if not username or not password:
            st.warning("Please enter both username and password.")
        elif username in st.session_state.users:
            st.error("Username already exists!")
        else:
            # Save new user persistently
            st.session_state.users[username] = password
            save_users(st.session_state.users)
            # Automatically log in the new user
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "dashboard"
            st.success(f"Sign-up successful! Welcome, {username}!")

    st.write("Already have an account?")
    if st.button("Go to Login", key="goto_login_btn"):
        st.session_state.page = "login"

# --- Login Page ---
def login_page():
    st.title("📈 MarketMind Login")
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/87/Logo_sample.png", width=150)

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    
    if st.button("Login", key="login_btn"):
        if st.session_state.users.get(username) == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "dashboard"
        else:
            st.error("Invalid credentials.")
    
    st.write("New user?")
    if st.button("Go to Sign Up", key="goto_signup_btn"):
        st.session_state.page = "signup"

# --- Dashboard Page ---
def dashboard_page():
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "login"

    st.title("📊 MarketMind Dashboard")
    st.write("Analyze market trends and get product recommendations")

    product_input = st.text_input("Enter product name:", key="product_input")
    if st.button("Analyze", key="analyze_btn") and product_input:
        product = product_input.strip().lower()
        trend_history = PRODUCTS_DB.get(product, [random.randint(20, 50) for _ in range(4)])
        trend, score = calculate_trend(trend_history)
        prediction, recommendation = predict_sales(score)

        # Display results
        st.subheader(f"Product: {product.title()}")
        st.write(f"**Trend:** {trend}")
        st.write(f"**Score:** {score}")
        st.write(f"**Prediction:** {prediction}")
        st.markdown(
            f"**Recommendation:** <span style='color: {'green' if recommendation=='Invest' else 'orange' if recommendation=='Hold' else 'red'}'>{recommendation}</span>",
            unsafe_allow_html=True
        )

        # Date-wise Trend Graph
        dates = pd.date_range(end=pd.Timestamp.today(), periods=4)
        df = pd.DataFrame({
            "Date": dates,
            "Trend Score": trend_history
        })
        df = df.set_index("Date")
        st.line_chart(df)

        # --- Product Overview ---
        overview_text = trend_overview(trend_history, product)
        st.markdown("### Product Overview")
        st.write(overview_text)

# --- Main App Flow ---
if st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "dashboard":
    if st.session_state.logged_in:
        dashboard_page()
    else:
        st.warning("Please log in first!")
        st.session_state.page = "login"
