import streamlit as st
import pandas as pd
import numpy as np
import random
import hashlib
import os
from sklearn.linear_model import LinearRegression
import plotly.express as px

st.set_page_config(page_title="MarketMind AI Ultra", layout="wide")

# -------------------------
# USER DATABASE
# -------------------------

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


# -------------------------
# SESSION MANAGEMENT
# -------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if not st.session_state.logged_in:

    st.title("🔐 MarketMind AI")

    tab1,tab2 = st.tabs(["Login","Signup"])

    with tab1:

        u = st.text_input("Username")
        p = st.text_input("Password",type="password")

        if st.button("Login"):

            if login(u,p):

                st.session_state.logged_in=True
                st.success("Login successful")
                st.rerun()

            else:
                st.error("Invalid credentials")

    with tab2:

        u = st.text_input("Create Username")
        p = st.text_input("Create Password",type="password")

        if st.button("Signup"):

            if signup(u,p):
                st.success("Account created")
            else:
                st.error("Username already exists")

    st.stop()

# -------------------------
# LOGOUT
# -------------------------

st.sidebar.button(
    "Logout",
    on_click=lambda: st.session_state.update({"logged_in":False})
)

# -------------------------
# PRODUCT DATABASE
# -------------------------

if "products_db" not in st.session_state:

    st.session_state.products_db={

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

# -------------------------
# MACHINE LEARNING MODEL
# -------------------------

def ml_predict(history,days=5):

    X=np.array(range(len(history))).reshape(-1,1)
    y=np.array(history)

    model=LinearRegression()
    model.fit(X,y)

    preds=[]

    for i in range(days):

        val=model.predict([[len(history)+i]])
        preds.append(round(float(val),2))

    return preds

# -------------------------
# DEMAND CLASSIFICATION
# -------------------------

def demand_level(score):

    if score>80:
        return "Very High 🔥"

    elif score>65:
        return "High 📈"

    elif score>50:
        return "Medium"

    else:
        return "Low 📉"


# -------------------------
# INVESTMENT ADVICE
# -------------------------

def investment_advice(score):

    if score>80:
        return "Invest 📈"

    elif score>60:
        return "Hold ⏳"

    else:
        return "Avoid ⚠️"


# -------------------------
# AI INSIGHT ENGINE
# -------------------------

def ai_insight(history):

    growth=history[-1]-history[-2]

    volatility=np.std(history)

    if growth>5:
        trend="Rapid Growth"

    elif growth>0:
        trend="Stable Growth"

    else:
        trend="Declining"

    if volatility<5:
        stability="Stable Market"

    else:
        stability="High Volatility"

    return trend,stability,growth


# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("📊 MarketMind AI Ultra")

menu=st.sidebar.radio(

    "Navigation",

    [
        "Dashboard",
        "Product Analysis",
        "Comparison",
        "Top Trends",
        "Market Scanner"
    ]

)

st.sidebar.write("### Products")

for p in PRODUCTS_DB:
    st.sidebar.write("•",p.title())

# -------------------------
# DASHBOARD
# -------------------------

if menu=="Dashboard":

    st.title("📊 AI Market Dashboard")

    total=len(PRODUCTS_DB)

    avg=int(np.mean([v[-1] for v in PRODUCTS_DB.values()]))

    top=max(PRODUCTS_DB,key=lambda x:PRODUCTS_DB[x][-1])

    growth={p:v[-1]-v[-2] for p,v in PRODUCTS_DB.items()}
    fastest=max(growth,key=growth.get)

    volatility={p:np.std(v) for p,v in PRODUCTS_DB.items()}
    most_stable=min(volatility,key=volatility.get)

    c1,c2,c3,c4,c5=st.columns(5)

    c1.metric("Products",total)
    c2.metric("Average Score",avg)
    c3.metric("Top Product",top.title())
    c4.metric("Fastest Growth",fastest.title())
    c5.metric("Most Stable",most_stable.title())

# -------------------------
# PRODUCT ANALYSIS
# -------------------------

elif menu=="Product Analysis":

    st.header("🔎 AI Product Analysis")

    product=st.text_input("Enter product")

    if st.button("Analyze") and product:

        product=product.strip().lower()

        history=PRODUCTS_DB.get(product)

        if history is None:

            base=random.randint(30,60)

            history=[base+i*random.randint(2,7) for i in range(6)]

            PRODUCTS_DB[product]=history

        score=history[-1]

        preds=ml_predict(history)

        trend,stability,growth=ai_insight(history)

        c1,c2,c3,c4,c5=st.columns(5)

        c1.metric("Score",score)
        c2.metric("Prediction",preds[0])
        c3.metric("Growth",growth)
        c4.metric("Demand",demand_level(score))
        c5.metric("Advice",investment_advice(score))

        # Trend chart
        dates=pd.date_range(end=pd.Timestamp.today(),periods=len(history))

        df=pd.DataFrame({
            "Date":dates,
            "Trend":history
        })

        fig=px.line(df,x="Date",y="Trend",title="Trend History")

        st.plotly_chart(fig,use_container_width=True)

        # Forecast chart
        fdf=pd.DataFrame({
            "Day":list(range(1,6)),
            "Prediction":preds
        })

        fig2=px.bar(fdf,x="Day",y="Prediction",title="AI Forecast")

        st.plotly_chart(fig2,use_container_width=True)

        st.subheader("🧠 AI Insights")

        st.write("Trend:",trend)
        st.write("Market Stability:",stability)

        csv=df.to_csv(index=False).encode()

        st.download_button(
            "Download Report",
            csv,
            f"{product}_report.csv",
            "text/csv"
        )

# -------------------------
# COMPARISON
# -------------------------

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

# -------------------------
# TOP TRENDS
# -------------------------

elif menu=="Top Trends":

    st.header("🔥 Top Products")

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
            "Demand":demand_level(v[-1]),
            "Advice":investment_advice(v[-1])

        })

    rdf=pd.DataFrame(data)

    st.dataframe(rdf)

# -------------------------
# MARKET SCANNER
# -------------------------

elif menu=="Market Scanner":

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

        sdf=pd.DataFrame(scan)
        st.dataframe(sdf)

    else:
        st.info("No strong trends detected")






