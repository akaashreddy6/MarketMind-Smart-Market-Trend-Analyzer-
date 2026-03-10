import streamlit as st
import pandas as pd
import numpy as np
import random
import hashlib
import os
import plotly.express as px

st.set_page_config(page_title="MarketMind AI", layout="wide")

# -----------------------------
# USER DATABASE
# -----------------------------

USER_FILE = "users.csv"

if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["username","password"]).to_csv(USER_FILE,index=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username,password):

    df = pd.read_csv(USER_FILE)

    if username in df["username"].values:
        return False

    new = pd.DataFrame({
        "username":[username],
        "password":[hash_password(password)]
    })

    df = pd.concat([df,new],ignore_index=True)
    df.to_csv(USER_FILE,index=False)

    return True

def login(username,password):

    df = pd.read_csv(USER_FILE)

    user = df[df["username"]==username]

    if not user.empty:
        if user.iloc[0]["password"] == hash_password(password):
            return True

    return False

# -----------------------------
# LOGIN SESSION
# -----------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 MarketMind AI")

    tab1,tab2 = st.tabs(["Login","Signup"])

    with tab1:

        username = st.text_input("Username")
        password = st.text_input("Password",type="password")

        if st.button("Login"):

            if login(username,password):
                st.session_state.logged_in=True
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:

        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password",type="password")

        if st.button("Signup"):

            if signup(new_user,new_pass):
                st.success("Account created. Please login.")
            else:
                st.error("Username already exists")

    st.stop()

# -----------------------------
# LOGOUT
# -----------------------------

st.sidebar.button(
    "Logout",
    on_click=lambda: st.session_state.update({"logged_in":False})
)

# -----------------------------
# PRODUCT DATABASE
# -----------------------------

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

# -----------------------------
# NUMPY AI PREDICTION
# -----------------------------

def predict_future(history,days=5):

    x = np.arange(len(history))
    y = np.array(history)

    slope, intercept = np.polyfit(x,y,1)

    predictions=[]

    for i in range(days):

        next_value = slope*(len(history)+i)+intercept
        predictions.append(round(next_value,2))

    return predictions

# -----------------------------
# DEMAND LEVEL
# -----------------------------

def demand(score):

    if score > 80:
        return "Very High 🔥"
    elif score > 65:
        return "High 📈"
    elif score > 50:
        return "Medium"
    else:
        return "Low 📉"

# -----------------------------
# INVESTMENT ADVICE
# -----------------------------

def investment(score):

    if score > 80:
        return "Invest 📈"
    elif score > 60:
        return "Hold ⏳"
    else:
        return "Avoid ⚠️"

# -----------------------------
# AI INSIGHT
# -----------------------------

def ai_insight(history):

    growth = history[-1] - history[-2]
    volatility = round(np.std(history),2)

    if growth > 5:
        trend = "Rapid Growth 🚀"
    elif growth > 0:
        trend = "Stable Growth 📈"
    else:
        trend = "Declining 📉"

    return trend, volatility, growth

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("📊 MarketMind AI")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard","Product Analysis","Comparison","Top Trends","Market Scanner"]
)

st.sidebar.write("### Products")

for p in PRODUCTS_DB:
    st.sidebar.write("•",p.title())

# -----------------------------
# DASHBOARD
# -----------------------------

if menu == "Dashboard":

    st.title("📊 AI Market Dashboard")

    total = len(PRODUCTS_DB)

    avg_score = int(np.mean([v[-1] for v in PRODUCTS_DB.values()]))

    top_product = max(PRODUCTS_DB,key=lambda x:PRODUCTS_DB[x][-1])

    growth_scores = {p:v[-1]-v[-2] for p,v in PRODUCTS_DB.items()}
    fastest = max(growth_scores,key=growth_scores.get)

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Products",total)
    col2.metric("Average Score",avg_score)
    col3.metric("Top Product",top_product.title())
    col4.metric("Fastest Growth",fastest.title())

# -----------------------------
# PRODUCT ANALYSIS
# -----------------------------

elif menu == "Product Analysis":

    st.header("🔎 Product AI Analysis")

    product = st.text_input("Enter product name")

    if st.button("Analyze") and product:

        product = product.strip().lower()

        history = PRODUCTS_DB.get(product)

        if history is None:

            base=random.randint(30,60)
            history=[base+i*random.randint(2,6) for i in range(6)]
            PRODUCTS_DB[product]=history

        score = history[-1]

        preds = predict_future(history)

        trend,volatility,growth = ai_insight(history)

        c1,c2,c3,c4,c5 = st.columns(5)

        c1.metric("Score",score)
        c2.metric("Prediction",preds[0])
        c3.metric("Growth",growth)
        c4.metric("Demand",demand(score))
        c5.metric("Advice",investment(score))

        dates = pd.date_range(end=pd.Timestamp.today(),periods=len(history))

        df = pd.DataFrame({
            "Date":dates,
            "Trend":history
        })

        fig = px.line(df,x="Date",y="Trend",title="Trend History")

        st.plotly_chart(fig,use_container_width=True)

        forecast_df = pd.DataFrame({
            "Day":[1,2,3,4,5],
            "Prediction":preds
        })

        fig2 = px.bar(forecast_df,x="Day",y="Prediction",title="AI Forecast")

        st.plotly_chart(fig2,use_container_width=True)

        st.subheader("🧠 AI Insights")

        st.write("Trend:",trend)
        st.write("Market Volatility:",volatility)

        csv = df.to_csv(index=False).encode()

        st.download_button(
            "Download Report",
            csv,
            f"{product}_report.csv",
            "text/csv"
        )

# -----------------------------
# COMPARISON
# -----------------------------

elif menu == "Comparison":

    st.header("⚔️ Product Comparison")

    plist=list(PRODUCTS_DB.keys())

    if len(plist)>=2:

        p1=st.selectbox("Product 1",plist)
        p2=st.selectbox("Product 2",plist,index=1)

        df=pd.DataFrame({
            p1:PRODUCTS_DB[p1],
            p2:PRODUCTS_DB[p2]
        })

        fig=px.line(df,title="Trend Comparison")

        st.plotly_chart(fig,use_container_width=True)

# -----------------------------
# TOP TRENDS
# -----------------------------

elif menu == "Top Trends":

    st.header("🔥 Top Trending Products")

    ranking=sorted(
        PRODUCTS_DB.items(),
        key=lambda x:x[1][-1],
        reverse=True
    )

    data=[]

    for p,v in ranking:

        data.append({
            "Product":p.title(),
            "Score":v[-1],
            "Demand":demand(v[-1]),
            "Advice":investment(v[-1])
        })

    st.dataframe(pd.DataFrame(data))

# -----------------------------
# MARKET SCANNER
# -----------------------------

elif menu == "Market Scanner":

    st.header("🛰️ Market Scanner")

    scan=[]

    for p,v in PRODUCTS_DB.items():

        growth=v[-1]-v[-2]

        if growth>5:

            scan.append({
                "Product":p.title(),
                "Growth":growth,
                "Signal":"🚀 Trending"
            })

    if scan:
        st.dataframe(pd.DataFrame(scan))
    else:
        st.info("No strong trends detected")







