import streamlit as st
import pandas as pd
import numpy as np
import random
import hashlib
import os
from sklearn.linear_model import LinearRegression
import plotly.express as px

st.set_page_config(page_title="MarketMind AI Pro", layout="wide")

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
# SESSION LOGIN
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 MarketMind AI Login")

    tab1,tab2 = st.tabs(["Login","Signup"])

    with tab1:

        user = st.text_input("Username")
        pw = st.text_input("Password",type="password")

        if st.button("Login"):

            if login(user,pw):
                st.session_state.logged_in=True
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:

        new_user = st.text_input("Create Username")
        new_pw = st.text_input("Create Password",type="password")

        if st.button("Signup"):

            if signup(new_user,new_pw):
                st.success("Account created")
            else:
                st.error("Username already exists")

    st.stop()

# -----------------------------
# LOGOUT
# -----------------------------
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in":False}))

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
# AI PREDICTION MODEL
# -----------------------------
def predict_ml(history,days=3):

    X = np.array(range(len(history))).reshape(-1,1)
    y = np.array(history)

    model = LinearRegression()
    model.fit(X,y)

    future=[]

    for i in range(days):
        pred = model.predict([[len(history)+i]])
        future.append(round(float(pred),2))

    return future

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
# SIDEBAR
# -----------------------------
st.sidebar.title("📊 MarketMind AI")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard","Product Analysis","Comparison","Top Trends"]
)

st.sidebar.write("### Products")

for p in PRODUCTS_DB:
    st.sidebar.write("•",p.title())

# -----------------------------
# DASHBOARD
# -----------------------------
if menu=="Dashboard":

    st.title("📊 MarketMind AI Pro Dashboard")

    total=len(PRODUCTS_DB)

    avg=int(np.mean([v[-1] for v in PRODUCTS_DB.values()]))

    top=max(PRODUCTS_DB,key=lambda x:PRODUCTS_DB[x][-1])

    growth={p:v[-1]-v[-2] for p,v in PRODUCTS_DB.items()}
    fastest=max(growth,key=growth.get)

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Products",total)
    col2.metric("Average Score",avg)
    col3.metric("Top Product",top.title())
    col4.metric("Fastest Growth",fastest.title())

# -----------------------------
# PRODUCT ANALYSIS
# -----------------------------
elif menu=="Product Analysis":

    st.header("🔎 Product AI Analysis")

    product = st.text_input("Enter product name")

    if st.button("Analyze") and product:

        product = product.strip().lower()

        history = PRODUCTS_DB.get(product)

        if history is None:

            base=random.randint(30,60)
            history=[base+i*random.randint(2,7) for i in range(4)]

            PRODUCTS_DB[product]=history

        score=history[-1]

        future=predict_ml(history)

        growth = history[-1]-history[-2]

        col1,col2,col3,col4,col5 = st.columns(5)

        col1.metric("Score",score)
        col2.metric("Prediction",future[0])
        col3.metric("Growth",growth)
        col4.metric("Demand",demand(score))
        col5.metric("Advice",investment(score))

        # Chart
        dates=pd.date_range(end=pd.Timestamp.today(),periods=len(history))

        df=pd.DataFrame({
            "Date":dates,
            "Trend":history
        })

        fig=px.line(df,x="Date",y="Trend",title="Market Trend")
        st.plotly_chart(fig,use_container_width=True)

        # Forecast
        fdf=pd.DataFrame({
            "Day":[1,2,3],
            "Prediction":future
        })

        fig2=px.bar(fdf,x="Day",y="Prediction",title="AI Forecast")
        st.plotly_chart(fig2,use_container_width=True)

        # Insight
        st.subheader("🧠 AI Market Insight")

        if growth > 5:
            st.success("Product demand is rapidly growing.")
        elif growth > 0:
            st.info("Stable market growth.")
        else:
            st.warning("Demand is decreasing.")

        # Download
        csv=df.to_csv(index=False).encode()

        st.download_button(
            "Download Report",
            csv,
            f"{product}_report.csv",
            "text/csv"
        )

# -----------------------------
# COMPARISON
# -----------------------------
elif menu=="Comparison":

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
elif menu=="Top Trends":

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

    rdf=pd.DataFrame(data)

    st.dataframe(rdf)








