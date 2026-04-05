import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ---------- PAGE ----------
st.set_page_config(page_title="Startup Growth Model", layout="centered")

st.title("📈 Startup Customer Growth with Churn")
st.write("Simulate how a startup gains and loses customers over time")

# ---------- INPUT ----------
st.header("🔧 Enter Details")

col1, col2 = st.columns(2)

with col1:
    total_market = st.number_input("Total Market Size", 100, 10000, 1000)
    initial_users = st.number_input("Initial Active Users", 1, 500, 50)

with col2:
    growth_rate = st.slider("Growth Rate (r)", 0.01, 1.0, 0.3)
    churn_rate = st.slider("Churn Rate (c)", 0.01, 1.0, 0.1)

time_steps = st.slider("Time (days)", 10, 100, 50)

# ---------- BUTTON ----------
run = st.button("🚀 Run Simulation")

# ---------- MODEL ----------
if run:

    active = [initial_users]
    churned = [0]

    for t in range(time_steps):

        new_users = growth_rate * active[-1] * (1 - active[-1] / total_market)
        lost_users = churn_rate * active[-1]

        active.append(active[-1] + new_users - lost_users)
        churned.append(churned[-1] + lost_users)

    # ---------- OUTPUT ----------
    st.success("✅ Simulation Completed")

    st.subheader("📊 Results")

    st.write(f"Peak Active Users: {int(max(active))}")
    st.write(f"Final Active Users: {int(active[-1])}")
    st.write(f"Total Churned Users: {int(churned[-1])}")

    # ---------- GRAPH ----------
    st.subheader("📈 Growth vs Churn Graph")

    fig, ax = plt.subplots()
    ax.plot(active, label="Active Users")
    ax.plot(churned, label="Churned Users")
    ax.set_xlabel("Time")
    ax.set_ylabel("Users")
    ax.legend()

    st.pyplot(fig)

    # ---------- INSIGHTS ----------
    st.subheader("🧠 Insights")

    if churn_rate > growth_rate:
        st.error("❌ High churn! Users are leaving faster than joining")
    else:
        st.success("✅ Healthy growth! Startup is scaling well")

    if max(active) > total_market * 0.8:
        st.warning("⚠️ Market saturation reached")