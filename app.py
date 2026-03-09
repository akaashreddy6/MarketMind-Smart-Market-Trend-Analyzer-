import streamlit as st
import random
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="MarketMind", layout="wide")

# --- Session state initialization ---
if "users" not in st.session_state:
    st.session_state.users = {"admin": "12345"}  # default user
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "signup"  # start with signup

# --- Product database ---
PRODUCTS_DB = {
    "smartphone": [70, 75, 80, 85],
    "laptop": [60, 65, 63, 68],
    "headphones": [50, 55, 60, 70],
    "book": [20, 25, 30, 28],
    "shoes": [40, 45, 50, 55],
}

# --- Utility Functions ---
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

# --- Sign Up Page ---
def signup_page():
    st.title("📝 Sign Up for MarketMind")
    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")
    if st.button("Sign Up"):
        if username in st.session_state.users:
            st.error("Username already exists! Try a different one.")
        elif not username or not password:
            st.warning("Please enter both username and password.")
        else:
            st.session_state.users[username] = password
            st.success("Sign-up successful! Please log in.")
            st.session_state.page = "login"
            st.experimental_rerun()  # <-- fixed: redirect to login immediately

# --- Login Page ---
def login_page():
    st.title("📈 MarketMind Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if st.session_state.users.get(username) == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "dashboard"
            st.success(f"Welcome {username}!")
            st.experimental_rerun()  # optional: rerun to refresh page
        else:
            st.error("Invalid credentials.")

# --- Dashboard Page ---
def dashboard_page():
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.page = "login"
        st.experimental_rerun()

    st.title("📊 MarketMind Dashboard")
    st.write("Analyze market trends and get product recommendations")

    product_input = st.text_input("Enter product name:")
    if st.button("Analyze") and product_input:
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

        # Trend Chart
        df = pd.DataFrame({
            "Week": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "Trend Score": trend_history
        })
        st.line_chart(df.set_index("Week"))

# --- Main ---
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
        st.experimental_rerun()

