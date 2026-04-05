import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Startup Customer Growth Dashboard",
    page_icon="🚀",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "run" not in st.session_state:
    st.session_state.run = False

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {
    background-color: #0f172a;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.big-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: white;
    margin-bottom: 0.2rem;
}
.sub-text {
    color: #94a3b8;
    font-size: 1rem;
    margin-bottom: 1.5rem;
}
.card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 18px;
    border-radius: 18px;
    text-align: center;
    color: white;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.08);
}
.section-box {
    background: rgba(255,255,255,0.03);
    padding: 18px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.05);
}
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #1e293b;
    color: white;
    border-radius: 10px;
    padding: 10px 18px;
}
.stTabs [aria-selected="true"] {
    background-color: #2563eb !important;
    color: white !important;
}
hr {
    border: none;
    height: 1px;
    background: rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Simulation Controls")

market_size = st.sidebar.slider("Total Market Size", 500, 20000, 5000, step=100)
growth_rate = st.sidebar.slider("Growth Rate", 0.01, 1.0, 0.25, step=0.01)
midpoint = st.sidebar.slider("Adoption Midpoint", 1, 50, 15)
churn_rate = st.sidebar.slider("Churn Rate", 0.0, 0.5, 0.08, step=0.01)
retention_rate = st.sidebar.slider("Retention Rate", 0.50, 1.00, 0.87, step=0.01)
time_steps = st.sidebar.slider("Time Steps", 12, 100, 40)
starting_customers = st.sidebar.slider("Starting Customers", 1, 500, 20)

st.sidebar.markdown("---")

if st.sidebar.button("🚀 Run Simulation", use_container_width=True):
    st.session_state.run = True

if st.sidebar.button("🔄 Reset Dashboard", use_container_width=True):
    st.session_state.run = False
    st.rerun()

# ---------------- HEADER ----------------
st.markdown("<div class='big-title'>🚀 Startup Customer Growth with Churn</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-text'>Logistic Growth + Churn Modeling + Retention Analysis + Business Insights</div>",
    unsafe_allow_html=True
)

if not st.session_state.run:
    st.info("👉 Adjust the parameters from the sidebar and click **Run Simulation**.")
    st.stop()

# ---------------- MODEL FUNCTIONS ----------------
def logistic_growth(t, K, r, t0):
    return K / (1 + np.exp(-r * (t - t0)))

def simulate_customers():
    t = np.arange(time_steps)

    # cumulative customer acquisition
    cumulative = logistic_growth(t, market_size, growth_rate, midpoint)

    # scale from starting customers
    cumulative = cumulative - cumulative[0] + starting_customers

    # new customers entering each step
    new_customers = np.diff(cumulative, prepend=starting_customers)

    active_hist = []
    churn_hist = []
    total_churned_hist = []
    active = starting_customers
    total_churned = 0

    for new in new_customers:
        churn = churn_rate * active
        active = max(active + new - churn, 0)
        total_churned += churn

        active_hist.append(active)
        churn_hist.append(churn)
        total_churned_hist.append(total_churned)

    return t, cumulative, new_customers, np.array(active_hist), np.array(churn_hist), np.array(total_churned_hist)

def retention_curve(retention, periods):
    return np.array([100 * (retention ** i) for i in range(periods)])

def estimate_parameters(observed, t_values):
    k_values = np.linspace(max(observed), max(observed) * 1.4, 12)
    r_values = np.linspace(0.05, 1.0, 18)
    t0_values = np.linspace(1, len(t_values), 18)

    best_error = float("inf")
    best_params = (0, 0, 0)

    for K in k_values:
        for r in r_values:
            for t0 in t0_values:
                pred = logistic_growth(t_values, K, r, t0)
                error = np.mean((observed - pred) ** 2)
                if error < best_error:
                    best_error = error
                    best_params = (K, r, t0)

    return best_params, best_error

# ---------------- SIMULATE ----------------
t, cumulative, new_customers, active, churned, total_churned = simulate_customers()
retention_data = retention_curve(retention_rate, time_steps)

np.random.seed(42)
observed_data = cumulative + np.random.normal(0, market_size * 0.02, len(cumulative))
observed_data = np.clip(observed_data, 0, None)

(best_K, best_r, best_t0), estimation_error = estimate_parameters(observed_data, t)

# ---------------- KPIs ----------------
peak_active = int(np.max(active))
final_active = int(active[-1])
final_acquired = int(cumulative[-1])
final_churned = int(total_churned[-1])
avg_new_customers = int(np.mean(new_customers))
final_retention = float(retention_data[-1])

# ---------------- METRIC CARDS ----------------
c1, c2, c3, c4, c5 = st.columns(5)

c1.markdown(f"<div class='card'><h3>{final_acquired}</h3><p>Total Acquired</p></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><h3>{final_active}</h3><p>Active Customers</p></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><h3>{final_churned}</h3><p>Total Churned</p></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><h3>{peak_active}</h3><p>Peak Active</p></div>", unsafe_allow_html=True)
c5.markdown(f"<div class='card'><h3>{final_retention:.1f}%</h3><p>End Retention</p></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Growth Dashboard", "📉 Retention", "🧠 Estimation", "💡 Insights"])

# ---------------- TAB 1 ----------------
with tab1:
    left, right = st.columns([2, 1])

    with left:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.subheader("Customer Growth Overview")

        fig, ax = plt.subplots(figsize=(11, 5))
        ax.plot(t, cumulative, label="Total Acquired", linewidth=3)
        ax.plot(t, active, label="Active Customers", linewidth=3)
        ax.plot(t, total_churned, label="Total Churned", linewidth=3)
        ax.bar(t, new_customers, alpha=0.25, label="New Customers")

        ax.set_title("Startup Customer Growth with Churn", fontsize=14, fontweight="bold")
        ax.set_xlabel("Time")
        ax.set_ylabel("Customers")
        ax.grid(True, alpha=0.25)
        ax.legend()
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.subheader("Quick Summary")
        st.metric("Average New Customers", avg_new_customers)
        st.metric("Growth Rate", f"{growth_rate:.2f}")
        st.metric("Churn Rate", f"{churn_rate:.2f}")
        st.metric("Retention Rate", f"{retention_rate:.2f}")

        if growth_rate > 0.5:
            st.success("Fast customer acquisition is happening.")
        else:
            st.warning("Growth is stable but not explosive.")

        if churn_rate > 0.20:
            st.error("High churn is reducing active customer base.")
        else:
            st.success("Churn is under reasonable control.")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- TAB 2 ----------------
with tab2:
    l1, l2 = st.columns([2, 1])

    with l1:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.subheader("Retention Curve")

        fig2, ax2 = plt.subplots(figsize=(11, 4.5))
        ax2.plot(t, retention_data, marker="o", linewidth=3)
        ax2.fill_between(t, retention_data, alpha=0.2)
        ax2.set_title("Retention Analysis Over Time", fontsize=14, fontweight="bold")
        ax2.set_xlabel("Time")
        ax2.set_ylabel("Retention %")
        ax2.grid(True, alpha=0.25)
        st.pyplot(fig2)
        st.markdown("</div>", unsafe_allow_html=True)

    with l2:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.subheader("Retention Health")

        if retention_rate >= 0.90:
            st.success("Excellent retention. Customers are sticking well.")
        elif retention_rate >= 0.80:
            st.info("Healthy retention. Product value seems strong.")
        else:
            st.warning("Retention needs improvement for sustainable growth.")

        st.write("**Interpretation:**")
        st.write("- High retention supports long-term startup growth.")
        st.write("- Low retention means customer acquisition alone is not enough.")
        st.write("- Reducing churn can improve active user curve faster than only increasing acquisition.")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- TAB 3 ----------------
with tab3:
    e1, e2 = st.columns([2, 1])

    with e1:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.subheader("Observed vs Estimated Growth")

        predicted_fit = logistic_growth(t, best_K, best_r, best_t0)

        fig3, ax3 = plt.subplots(figsize=(11, 4.8))
        ax3.plot(t, observed_data, "o", label="Observed Data", alpha=0.8)
        ax3.plot(t, predicted_fit, linewidth=3, label="Estimated Logistic Fit")
        ax3.set_title("Parameter Estimation", fontsize=14, fontweight="bold")
        ax3.set_xlabel("Time")
        ax3.set_ylabel("Customers")
        ax3.grid(True, alpha=0.25)
        ax3.legend()
        st.pyplot(fig3)
        st.markdown("</div>", unsafe_allow_html=True)

    with e2:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        st.subheader("Estimated Parameters")
        st.metric("Estimated K", f"{best_K:.0f}")
        st.metric("Estimated r", f"{best_r:.2f}")
        st.metric("Estimated t₀", f"{best_t0:.2f}")
        st.metric("Estimation Error", f"{estimation_error:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- TAB 4 ----------------
with tab4:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.subheader("Business Insights")

    if final_active > 0.7 * final_acquired:
        st.success("A large share of acquired customers are still active. This suggests strong product stickiness.")
    else:
        st.warning("A significant number of acquired customers are not staying active.")

    if churn_rate > 0.15 and retention_rate < 0.80:
        st.error("The startup may struggle to scale unless churn reduction becomes a priority.")
    elif growth_rate > 0.4 and retention_rate > 0.85:
        st.success("This is a strong startup growth pattern with healthy retention and scalable momentum.")
    else:
        st.info("Growth exists, but improving retention can make the model much stronger.")

    st.write("### Recommended Strategy")
    st.write("- Improve onboarding to reduce early churn")
    st.write("- Build product habit loops to increase retention")
    st.write("- Track active vs churned users weekly")
    st.write("- Balance acquisition spend with customer retention effort")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Developed with Streamlit | Startup Growth Mathematical Modeling Dashboard")
