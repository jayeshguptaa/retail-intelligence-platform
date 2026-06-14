import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stApp { background-color: #f8f9fa; }

    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    [data-testid="metric-container"] label {
        font-size: 13px !important;
        color: #6c757d !important;
        font-weight: 500 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #212529 !important;
    }

    .section-header {
        font-size: 18px;
        font-weight: 700;
        color: #212529;
        margin: 28px 0 8px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #4361ee;
        display: inline-block;
    }

    .insight-box {
        background: white;
        border-left: 4px solid #4361ee;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 8px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        font-size: 14px;
        color: #333;
        line-height: 1.6;
    }
    .insight-box.warning { border-left-color: #f4a261; }
    .insight-box.success { border-left-color: #2d6a4f; }
    .insight-box.danger  { border-left-color: #e63946; }

    .dashboard-title {
        font-size: 28px;
        font-weight: 800;
        color: #212529;
        margin-bottom: 4px;
    }
    .dashboard-subtitle {
        font-size: 14px;
        color: #6c757d;
        margin-bottom: 20px;
    }

    section[data-testid="stSidebar"] { background-color: #1e2a4a; }
    section[data-testid="stSidebar"] * { color: white !important; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: white;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 500;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background: #4361ee !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv("retail_sales_data.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Year"] = df["Order Date"].dt.year
    df["Month Number"] = df["Order Date"].dt.month
    df["Month Name"] = df["Order Date"].dt.strftime("%B")
    df["Quarter"] = df["Order Date"].dt.quarter.map({
        1: "Q1 (Jan–Mar)",
        2: "Q2 (Apr–Jun)",
        3: "Q3 (Jul–Sep)",
        4: "Q4 (Oct–Dec)"
    })
    df["Is Returned"] = df["Returned"].map({"Yes": 1, "No": 0})
    return df

df = load_data()

with st.sidebar:
    st.markdown("## 🛒 Sales Dashboard")
    st.markdown("---")

    selected_years = st.multiselect(
        "Year", sorted(df["Year"].unique().tolist()),
        default=sorted(df["Year"].unique().tolist())
    )
    selected_cities = st.multiselect(
        "City", sorted(df["City"].unique().tolist()),
        default=sorted(df["City"].unique().tolist())
    )
    selected_categories = st.multiselect(
        "Product Category", sorted(df["Product Category"].unique().tolist()),
        default=sorted(df["Product Category"].unique().tolist())
    )

    st.markdown("---")
    st.markdown("""
    **Dataset**
    - 2,000 sales records
    - Jan 2023 – Jun 2024
    - 8 Indian cities · 5 categories
    """)

filtered = df[
    df["Year"].isin(selected_years) &
    df["City"].isin(selected_cities) &
    df["Product Category"].isin(selected_categories)
]

st.markdown('<div class="dashboard-title">🛒 Retail Sales Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">2,000 orders · 8 Indian cities · Jan 2023 – Jun 2024</div>', unsafe_allow_html=True)

total_revenue = filtered["Total Revenue (INR)"].sum()
total_profit  = filtered["Profit (INR)"].sum()
total_orders  = len(filtered)
profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
avg_order_val = total_revenue / total_orders if total_orders > 0 else 0
return_rate   = filtered["Is Returned"].mean() * 100
avg_rating    = filtered["Customer Rating"].mean()

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("💰 Total Revenue", f"₹{total_revenue/1_000_000:.2f}M")
with col2: st.metric("📈 Total Profit", f"₹{total_profit/1_000_000:.2f}M")
with col3: st.metric("🧾 Orders", f"{total_orders:,}")
with col4: st.metric("💹 Profit Margin", f"{profit_margin:.1f}%")

col5, col6, col7, col8 = st.columns(4)
with col5: st.metric("🛒 Avg Order Value", f"₹{avg_order_val:,.0f}")
with col6: st.metric("↩️ Return Rate", f"{return_rate:.1f}%")
with col7: st.metric("⭐ Avg Rating", f"{avg_rating:.2f} / 5")
with col8:
    top_city = filtered.groupby("City")["Total Revenue (INR)"].sum().idxmax() if not filtered.empty else "—"
    st.metric("🏆 Top City", top_city)

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Sales Over Time",
    "🛍️ Product Performance",
    "🏙️ City Analysis",
    "👥 Customer Behaviour",
    "🔍 Insights"
])

# ── TAB 1: SALES OVER TIME ────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Monthly Revenue & Profit</div>', unsafe_allow_html=True)

    monthly = (
        filtered.groupby(["Year", "Month Number", "Month Name"])
        .agg(Revenue=("Total Revenue (INR)", "sum"), Orders=("Order ID", "count"), Profit=("Profit (INR)", "sum"))
        .reset_index()
        .sort_values(["Year", "Month Number"])
    )
    monthly["Label"] = monthly["Month Name"].str[:3] + " " + monthly["Year"].astype(str)

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=monthly["Label"], y=monthly["Revenue"],
        name="Revenue (₹)", marker_color="#4361ee",
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>"
    ))
    fig1.add_trace(go.Scatter(
        x=monthly["Label"], y=monthly["Profit"],
        name="Profit (₹)", line=dict(color="#2d6a4f", width=2.5),
        mode="lines+markers",
        hovertemplate="<b>%{x}</b><br>Profit: ₹%{y:,.0f}<extra></extra>"
    ))
    fig1.update_layout(
        height=380, plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, title="Month"),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", title="Amount (₹)"),
        margin=dict(t=20, b=40, l=60, r=20)
    )
    st.plotly_chart(fig1, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-header">Revenue by Quarter</div>', unsafe_allow_html=True)
        quarterly = filtered.groupby("Quarter").agg(Revenue=("Total Revenue (INR)", "sum")).reset_index()
        fig_q = px.bar(quarterly, x="Quarter", y="Revenue", color="Quarter",
                       color_discrete_sequence=["#4361ee","#3a86ff","#48cae4","#90e0ef"],
                       labels={"Revenue": "Revenue (₹)"})
        fig_q.update_layout(height=320, showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f0f0f0"))
        st.plotly_chart(fig_q, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Orders by Day of Week</div>', unsafe_allow_html=True)
        filtered["Day of Week"] = filtered["Order Date"].dt.day_name()
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_data = filtered.groupby("Day of Week")["Order ID"].count().reindex(day_order).reset_index()
        day_data.columns = ["Day", "Orders"]
        fig_day = px.bar(day_data, x="Day", y="Orders", color="Orders",
                         color_continuous_scale=["#d0e8ff","#4361ee"],
                         labels={"Orders": "Orders", "Day": ""})
        fig_day.update_layout(height=320, showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                              coloraxis_showscale=False,
                              xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f0f0f0"))
        st.plotly_chart(fig_day, use_container_width=True)

# ── TAB 2: PRODUCT PERFORMANCE ───────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Revenue & Profit by Category</div>', unsafe_allow_html=True)

    cat_data = filtered.groupby("Product Category").agg(
        Revenue=("Total Revenue (INR)", "sum"),
        Profit=("Profit (INR)", "sum"),
        Orders=("Order ID", "count"),
        Avg_Rating=("Customer Rating", "mean"),
        Return_Rate=("Is Returned", "mean")
    ).reset_index()
    cat_data["Profit Margin (%)"] = (cat_data["Profit"] / cat_data["Revenue"] * 100).round(1)
    cat_data["Return Rate (%)"]   = (cat_data["Return_Rate"] * 100).round(1)
    cat_data["Avg Rating"]        = cat_data["Avg_Rating"].round(2)

    col_a, col_b = st.columns(2)
    with col_a:
        fig_cat = px.bar(cat_data.sort_values("Revenue"), x="Revenue", y="Product Category",
                         orientation="h", color="Profit",
                         color_continuous_scale=["#ffd166","#06d6a0"],
                         labels={"Revenue": "Revenue (₹)", "Product Category": "", "Profit": "Profit (₹)"},
                         title="Revenue vs Profit by Category")
        fig_cat.update_layout(height=350, plot_bgcolor="white", paper_bgcolor="white",
                              xaxis=dict(showgrid=True, gridcolor="#f0f0f0"), yaxis=dict(showgrid=False))
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_b:
        fig_pie = px.pie(cat_data, values="Revenue", names="Product Category",
                         color_discrete_sequence=["#4361ee","#3a86ff","#06d6a0","#ffd166","#ef476f"],
                         title="Revenue Share by Category")
        fig_pie.update_traces(textposition="inside", textinfo="percent+label",
                              hovertemplate="<b>%{label}</b><br>Revenue: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>")
        fig_pie.update_layout(height=350, showlegend=False, paper_bgcolor="white")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('<div class="section-header">Top 10 Products by Profit</div>', unsafe_allow_html=True)

    prod_data = filtered.groupby(["Product Name", "Product Category"]).agg(
        Revenue=("Total Revenue (INR)", "sum"),
        Profit=("Profit (INR)", "sum"),
        Units=("Quantity Sold", "sum"),
        Rating=("Customer Rating", "mean"),
        Returns=("Is Returned", "mean")
    ).reset_index().sort_values("Profit", ascending=False).head(10)
    prod_data["Rating"] = prod_data["Rating"].round(2)
    prod_data["Return Rate (%)"] = (prod_data["Returns"] * 100).round(1)

    fig_prod = px.bar(prod_data.sort_values("Profit"), x="Profit", y="Product Name",
                      orientation="h", color="Product Category",
                      color_discrete_sequence=["#4361ee","#3a86ff","#06d6a0","#ffd166","#ef476f"],
                      labels={"Profit": "Total Profit (₹)", "Product Name": ""},
                      title="Top 10 Products by Profit")
    fig_prod.update_layout(height=400, plot_bgcolor="white", paper_bgcolor="white",
                           xaxis=dict(showgrid=True, gridcolor="#f0f0f0"), yaxis=dict(showgrid=False))
    st.plotly_chart(fig_prod, use_container_width=True)

    st.markdown('<div class="section-header">Return Rate by Category</div>', unsafe_allow_html=True)

    return_data = filtered.groupby("Product Category").agg(Returns=("Is Returned", "mean")).reset_index()
    return_data["Return Rate (%)"] = (return_data["Returns"] * 100).round(1)
    return_data["Level"] = return_data["Return Rate (%)"].apply(
        lambda x: "High (>8%)" if x > 8 else ("Medium (5–8%)" if x > 5 else "Low (<5%)")
    )
    fig_ret = px.bar(return_data.sort_values("Return Rate (%)"), x="Product Category", y="Return Rate (%)",
                     color="Level",
                     color_discrete_map={"High (>8%)": "#e63946", "Medium (5–8%)": "#f4a261", "Low (<5%)": "#2d6a4f"},
                     labels={"Return Rate (%)": "Return Rate (%)", "Product Category": ""},
                     title="Return Rate by Category")
    fig_ret.update_layout(height=320, plot_bgcolor="white", paper_bgcolor="white",
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
                          legend_title="Level")
    st.plotly_chart(fig_ret, use_container_width=True)

# ── TAB 3: CITY ANALYSIS ─────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Revenue by City</div>', unsafe_allow_html=True)

    city_data = filtered.groupby("City").agg(
        Revenue=("Total Revenue (INR)", "sum"),
        Profit=("Profit (INR)", "sum"),
        Orders=("Order ID", "count"),
        Avg_Discount=("Discount Percentage", "mean"),
        Return_Rate=("Is Returned", "mean"),
        Avg_Rating=("Customer Rating", "mean")
    ).reset_index().sort_values("Revenue", ascending=False)
    city_data["Profit Margin (%)"]   = (city_data["Profit"] / city_data["Revenue"] * 100).round(1)
    city_data["Return Rate (%)"]     = (city_data["Return_Rate"] * 100).round(1)
    city_data["Average Discount (%)"] = city_data["Avg_Discount"].round(1)
    city_data["Average Rating"]       = city_data["Avg_Rating"].round(2)

    col_a, col_b = st.columns(2)
    with col_a:
        fig_city = px.bar(city_data.sort_values("Revenue"), x="Revenue", y="City",
                          orientation="h", color="Revenue",
                          color_continuous_scale=["#d0e8ff","#4361ee"],
                          labels={"Revenue": "Revenue (₹)", "City": ""},
                          title="Total Revenue by City")
        fig_city.update_layout(height=380, showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                               coloraxis_showscale=False,
                               xaxis=dict(showgrid=True, gridcolor="#f0f0f0"), yaxis=dict(showgrid=False))
        st.plotly_chart(fig_city, use_container_width=True)

    with col_b:
        fig_city2 = px.scatter(city_data, x="Revenue", y="Profit Margin (%)",
                               size="Orders", color="City", text="City",
                               color_discrete_sequence=px.colors.qualitative.Set2,
                               labels={"Revenue": "Revenue (₹)"},
                               title="Revenue vs Profit Margin by City")
        fig_city2.update_traces(textposition="top center", textfont_size=10)
        fig_city2.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
                                xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
                                yaxis=dict(showgrid=True, gridcolor="#f0f0f0"))
        st.plotly_chart(fig_city2, use_container_width=True)

    st.markdown('<div class="section-header">City Performance Summary</div>', unsafe_allow_html=True)

    display_city = city_data[["City","Orders","Revenue","Profit","Profit Margin (%)","Average Discount (%)","Return Rate (%)","Average Rating"]].copy()
    display_city["Revenue"] = display_city["Revenue"].apply(lambda x: f"₹{x:,.0f}")
    display_city["Profit"]  = display_city["Profit"].apply(lambda x: f"₹{x:,.0f}")
    display_city = display_city.rename(columns={"Orders": "Total Orders", "Revenue": "Total Revenue", "Profit": "Total Profit"})
    st.dataframe(display_city, use_container_width=True, hide_index=True)

# ── TAB 4: CUSTOMER BEHAVIOUR ────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Revenue by Gender & Payment Method</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        gender_data = filtered.groupby("Customer Gender").agg(Revenue=("Total Revenue (INR)", "sum")).reset_index()
        fig_g = px.pie(gender_data, values="Revenue", names="Customer Gender",
                       color_discrete_sequence=["#4361ee","#ef476f"],
                       title="Revenue by Customer Gender")
        fig_g.update_traces(textinfo="percent+label", textposition="inside")
        fig_g.update_layout(height=320, showlegend=False, paper_bgcolor="white")
        st.plotly_chart(fig_g, use_container_width=True)

    with col_b:
        pay_data = filtered.groupby("Payment Method")["Order ID"].count().reset_index()
        pay_data.columns = ["Payment Method", "Orders"]
        fig_pay = px.bar(pay_data.sort_values("Orders"), x="Orders", y="Payment Method",
                         orientation="h", color="Orders",
                         color_continuous_scale=["#d0e8ff","#4361ee"],
                         title="Orders by Payment Method")
        fig_pay.update_layout(height=320, showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                              coloraxis_showscale=False,
                              xaxis=dict(showgrid=True, gridcolor="#f0f0f0"), yaxis=dict(showgrid=False))
        st.plotly_chart(fig_pay, use_container_width=True)

    st.markdown('<div class="section-header">Revenue by Age Group & Category</div>', unsafe_allow_html=True)

    filtered["Age Group"] = pd.cut(filtered["Customer Age"],
        bins=[17, 25, 35, 45, 55, 100],
        labels=["18–25", "26–35", "36–45", "46–55", "56+"]
    )
    age_cat = filtered.groupby(["Age Group", "Product Category"])["Total Revenue (INR)"].sum().reset_index()
    fig_age = px.bar(age_cat, x="Age Group", y="Total Revenue (INR)", color="Product Category",
                     color_discrete_sequence=["#4361ee","#3a86ff","#06d6a0","#ffd166","#ef476f"],
                     labels={"Total Revenue (INR)": "Revenue (₹)", "Age Group": "Age Group"},
                     barmode="stack", title="Revenue by Age Group")
    fig_age.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
                          legend_title="Category")
    st.plotly_chart(fig_age, use_container_width=True)

    st.markdown('<div class="section-header">Discount vs Orders</div>', unsafe_allow_html=True)

    discount_data = filtered.groupby("Discount Percentage").agg(
        Orders=("Order ID", "count"),
        Avg_Revenue=("Total Revenue (INR)", "mean")
    ).reset_index()
    fig_disc = px.scatter(discount_data, x="Discount Percentage", y="Orders",
                          size="Avg_Revenue", color="Discount Percentage",
                          color_continuous_scale=["#4361ee","#ef476f"],
                          labels={"Discount Percentage": "Discount (%)", "Orders": "Number of Orders"},
                          title="Discount % vs Orders (bubble size = avg order value)")
    fig_disc.update_layout(height=340, plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False,
                           xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
                           yaxis=dict(showgrid=True, gridcolor="#f0f0f0"))
    st.plotly_chart(fig_disc, use_container_width=True)

# ── TAB 5: INSIGHTS ───────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-header">Key Findings</div>', unsafe_allow_html=True)

    top_cat      = filtered.groupby("Product Category")["Total Revenue (INR)"].sum().idxmax()
    worst_ret    = filtered.groupby("Product Category")["Is Returned"].mean().idxmax()
    worst_ret_rt = filtered.groupby("Product Category")["Is Returned"].mean().max() * 100
    top_pay      = filtered.groupby("Payment Method")["Order ID"].count().idxmax()

    st.markdown("#### What's Working")
    st.markdown(f"""
    <div class="insight-box success">
    <b>{top_cat} leads on revenue and margin.</b> Customers purchase at full price — discounting in this category directly reduces profit without driving incremental volume.
    </div>
    <div class="insight-box success">
    <b>Overall profit margin is {profit_margin:.1f}%.</b> Healthy performance, but at risk if the current discount structure is left unchanged.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### What Needs Attention")
    st.markdown(f"""
    <div class="insight-box danger">
    <b>{worst_ret} has a {worst_ret_rt:.1f}% return rate.</b> Each return carries a double cost — outbound and inbound logistics. Worth investigating whether the issue is product quality, packaging, or a mismatch between listing descriptions and the actual product.
    </div>
    <div class="insight-box warning">
    <b>Discounts are being applied across all order values.</b> The data shows comparable order volumes at 0% and higher discount tiers, which suggests a blanket discount policy is compressing margins without meaningful lift in conversions.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Recommendations")

    actions = [
        ("1", "Investigate returns in high-return categories",
         f"A return rate above 8% in {worst_ret} indicates a process issue. Check whether it correlates with specific suppliers, SKUs, or cities — then look at product descriptions, packaging quality, and delivery condition on arrival.",
         "#e63946"),
        ("2", "Switch to targeted discounting",
         "Sales volume holds at low and zero discount levels, meaning blanket discounts are unnecessary. Reserve discounts for slow-moving inventory, defined seasonal windows, and loyalty rewards for repeat customers.",
         "#f4a261"),
        ("3", f"Protect the {top_cat} margin",
         f"{top_cat} is the primary profit driver. Ensure consistent stock availability, prioritise it in marketing, and avoid applying automatic discounts that erode the margin on the highest-value category.",
         "#4361ee"),
        ("4", f"Leverage {top_pay} adoption",
         f"{top_pay} already leads on payment method share. A small cashback incentive on {top_pay} transactions above a threshold can increase digital payment adoption while reducing transaction costs relative to card networks.",
         "#2d6a4f"),
        ("5", "Plan for Q4 demand spike",
         "October and November show a consistent sales uptick. Inventory procurement, staffing, and logistics capacity should be adjusted by September to avoid stockouts during the peak window.",
         "#7b2d8b"),
    ]

    for num, title, desc, color in actions:
        st.markdown(f"""
        <div style="background:white;border-left:4px solid {color};border-radius:8px;padding:16px 20px;
                    margin:10px 0;box-shadow:0 2px 6px rgba(0,0,0,0.06)">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                <span style="background:{color};color:white;border-radius:50%;width:26px;height:26px;
                             display:inline-flex;align-items:center;justify-content:center;
                             font-weight:700;font-size:13px;flex-shrink:0">{num}</span>
                <span style="font-weight:600;font-size:14px;color:#212529">{title}</span>
            </div>
            <div style="font-size:13px;color:#555;line-height:1.7;margin-left:36px">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Raw Data")
    show_cols = ["Order ID","Order Date","City","Customer Gender","Customer Age",
                 "Product Category","Product Name","Quantity Sold","Selling Price (INR)",
                 "Total Revenue (INR)","Profit (INR)","Payment Method","Returned","Customer Rating"]
    st.dataframe(filtered[show_cols].sort_values("Order Date", ascending=False),
                 use_container_width=True, height=400)

    st.markdown("---")
    st.caption("Python · Pandas · SQLite · Streamlit · Plotly  |  2,000 retail transactions  |  Jan 2023 – Jun 2024")
