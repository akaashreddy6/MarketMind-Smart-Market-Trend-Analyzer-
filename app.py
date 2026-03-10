import streamlit as st
import pandas as pd
import numpy as np
import random
import hashlib
import os

st.set_page_config(page_title="MarketMind AI", layout="wide")

# ---------- User File ----------
USER_FILE = "users.csv"

if not os.path.exists(USER_FILE):
    df = pd.DataFrame(columns=["username","password"])
    df.to_csv(USER_FILE,index=False)

# ---------- Password Hash ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- Signup ----------
def signup(username,password):
    df = pd.read_csv(USER_FILE)

    if username in df["username"].values:
        return False

    new_user = pd.DataFrame({
        "username":[username],
        "password":[hash_password(password)]
    })

    df = pd.concat([df,new_user],ignore_index=True)
    df.to_csv(USER_FILE,index=False)

    return True

# ---------- Login ----------
def login(username,password):

    df = pd.read_csv(USER_FILE)

    user = df[df["username"]==username]

    if not user.empty:

        if user.iloc[0]["password"] == hash_password(password):
            return True

    return False

# ---------- Session ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- Login / Signup UI ----------
if not st.session_state.logged_in:

    st.title("🔐 MarketMind AI Login")

    tab1,tab2 = st.tabs(["Login","Signup"])

    # LOGIN
    with tab1:

        username = st.text_input("Username")
        password = st.text_input("Password",type="password")

        if st.button("Login"):

            if login(username,password):

                st.session_state.logged_in = True
                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Invalid credentials")

    # SIGNUP
    with tab2:

        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password",type="password")

        if st.button("Signup"):

            if signup(new_user,new_pass):
                st.success("Account Created. Please Login.")
            else:
                st.error("Username already exists")

    st.stop()

# ---------- Logout ----------
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in":False}))

# ---------- Product Database ----------
if "products_db" not in st.session_state:

    st.session_state.products_db = {
        "smartphone":[70,75,80,85],
        "laptop":[60,65,63,68],
        "headphones":[50,55,60,70],
        "shoes":[40,45,50,55],
        "tablet":[65,70,72,78],
        "smartwatch":[55,60,64,69],
        "camera":[50,52,55,60],
        "gaming console":[75,78,82,90]
    }

PRODUCTS_DB = st.session_state.products_db

# ---------- Prediction ----------
def predict_future(history,days=3):

    avg_growth = np.mean(np.diff(history))
    last_value = history[-1]

    predictions = []

    for i in range(days):
        last_value += avg_growth
        predictions.append(round(last_value,2))

    return predictions

# ---------- Demand ----------
def demand_score(score):

    if score > 80:
        return "Very High 🔥"
    elif score > 65:
        return "High 📈"
    elif score > 50:
        return "Medium ➖"
    else:
        return "Low 📉"

# ---------- Investment Advice ----------
def investment_advice(score):

    if score > 80:
        return "Invest 📈"
    elif score > 60:
        return "Hold ⏳"
    else:
        return "Avoid ⚠️"

# ---------- Sidebar ----------
st.sidebar.title("📊 MarketMind AI")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard","Product Analysis","Product Comparison","Top Trends"]
)

st.sidebar.write("### Tracked Products")

for p in PRODUCTS_DB:
    st.sidebar.write("•",p.title())

# ---------- Dashboard ----------
if menu == "Dashboard":

    st.title("📊 MarketMind AI Dashboard")

    total_products = len(PRODUCTS_DB)

    avg_score = int(np.mean([v[-1] for v in PRODUCTS_DB.values()]))

    top_product = max(PRODUCTS_DB, key=lambda x: PRODUCTS_DB[x][-1])

    growth_scores = {p:v[-1]-v[-2] for p,v in PRODUCTS_DB.items()}
    fastest = max(growth_scores,key=growth_scores.get)

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Products Tracked",total_products)
    col2.metric("Average Trend Score",avg_score)
    col3.metric("Top Product",top_product.title())
    col4.metric("Fastest Growth",fastest.title())

# ---------- Product Analysis ----------
elif menu == "Product Analysis":

    st.header("🔍 Product Trend Analysis")

    product = st.text_input("Enter product name")

    if st.button("Analyze Product") and product:

        product = product.strip().lower()

        history = PRODUCTS_DB.get(product)

        if history is None:

            base = random.randint(30,60)
            history = [base + i*random.randint(2,6) for i in range(4)]
            PRODUCTS_DB[product] = history

        score = history[-1]

        future = predict_future(history)

        demand = demand_score(score)

        advice = investment_advice(score)

        growth = history[-1] - history[-2]

        col1,col2,col3,col4,col5 = st.columns(5)

        col1.metric("Current Score",score)
        col2.metric("Next Prediction",future[0])
        col3.metric("Growth",growth)
        col4.metric("Demand Level",demand)
        col5.metric("Investment",advice)

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
            f"{product}_report.csv",
            "text/csv"
        )

# ---------- Product Comparison ----------
elif menu == "Product Comparison":

    st.header("⚔️ Compare Products")

    products_list = list(PRODUCTS_DB.keys())

    if len(products_list) >= 2:

        p1 = st.selectbox("Product 1",products_list)
        p2 = st.selectbox("Product 2",products_list,index=1)

        df = pd.DataFrame({
            p1:PRODUCTS_DB[p1],
            p2:PRODUCTS_DB[p2]
        })

        st.line_chart(df)

# ---------- Top Trends ----------
elif menu == "Top Trends":

    st.header("🔥 Top Trending Products")

    ranking = sorted(PRODUCTS_DB.items(),
                     key=lambda x:x[1][-1],
                     reverse=True)

    ranking_df = pd.DataFrame([
        {
            "Product":p.title(),
            "Score":data[-1],
            "Advice":investment_advice(data[-1])
        }
        for p,data in ranking
    ])

    st.dataframe(ranking_df)








