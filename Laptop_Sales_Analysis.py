# ================================
# Laptop Sales Analysis Dashboard (FINAL UI + ALL FEATURES)
# ================================

import pandas as pd
import streamlit as st
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')
import base64

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Laptop Sales Analysis", page_icon="💻", layout="wide")
st.title("💻 Laptop Sales Analysis Dashboard")

# -------------------------------
# Background Image
# -------------------------------
with open("background_image.jpg", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode()

# -------------------------------
# CSS
# -------------------------------
st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{img_base64}");
    background-size: cover;
    background-attachment: fixed;
}}

[data-testid="stAppViewContainer"] {{
    background: rgba(0,0,0,0.7);
}}

section[data-testid="stSidebar"] {{
    background: rgba(0,0,0,0.4);
    backdrop-filter: blur(12px);
    color: white;
}}

.kpi-card {{
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    backdrop-filter: blur(10px);
    color: white;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Helper
# -------------------------------
def format_number(num):
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    else:
        return f"{num:.0f}"

# -------------------------------
# Load Data
# -------------------------------
df = pd.read_csv("Laptop Sales Data.csv")

# -------------------------------
# Filters
# -------------------------------
st.sidebar.header("🔍 Filters")

year = st.sidebar.multiselect("Select Year", sorted(df["Year"].dropna().unique()))
temp_df = df[df["Year"].isin(year)] if year else df

brand = st.sidebar.multiselect("Select Brand", sorted(temp_df["Brand"].dropna().unique()))
filtered_df = temp_df[temp_df["Brand"].isin(brand)] if brand else temp_df

# -------------------------------
# KPI
# -------------------------------
total_sales = filtered_df["Sales"].sum()
total_quantity = filtered_df["Quantity_Sold"].sum()
avg_price = filtered_df["Price"].mean()

k1, k2, k3 = st.columns(3)

k1.markdown(f"<div class='kpi-card'><h3>Total Sales</h3><h2>₹ {format_number(total_sales)}</h2></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='kpi-card'><h3>Avg Price</h3><h2>₹ {format_number(avg_price)}</h2></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='kpi-card'><h3>Total Quantity</h3><h2>{format_number(total_quantity)}</h2></div>", unsafe_allow_html=True)

st.divider()

# -------------------------------
# Brand + Monthly Charts
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Brand Wise Sales")
    brand_df = filtered_df.groupby("Brand")["Sales"].sum().reset_index()
    brand_df["label"] = brand_df["Sales"].apply(format_number)

    fig1 = px.bar(brand_df, x="Brand", y="Sales", text="label")
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig1, use_container_width=True)

    v1, d1 = st.columns(2)
    with v1:
        with st.expander("View Data"):
            st.dataframe(brand_df)
    with d1:
        st.download_button("Download", brand_df.to_csv(index=False), "brand_sales.csv")

with col2:
    st.subheader("📈 Monthly Sales Trend")
    filtered_df["Month"] = pd.to_datetime(filtered_df["Month"])
    trend = filtered_df.groupby("Month")["Sales"].sum().reset_index()

    fig2 = px.line(trend, x="Month", y="Sales", markers=True)
    fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig2, use_container_width=True)

    v2, d2 = st.columns(2)
    with v2:
        with st.expander("View Data"):
            st.dataframe(trend)
    with d2:
        st.download_button("Download", trend.to_csv(index=False), "monthly_sales.csv")

st.divider()

# -------------------------------
# Pie & Donut
# -------------------------------
c1, c2 = st.columns(2)

pie_df = filtered_df.groupby("Region")["Sales"].sum().reset_index()
donut_df = filtered_df.groupby("Region")["Quantity_Sold"].sum().reset_index()

with c1:
    st.subheader("🥧 Region Wise Sales")
    fig3 = px.pie(pie_df, values="Sales", names="Region")
    fig3.update_traces(textposition='outside', pull=[0.1]*len(pie_df))
    fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("View Data"):
        st.dataframe(pie_df)
    st.download_button("Download", pie_df.to_csv(index=False), "region_sales.csv")

with c2:
    st.subheader("🍩 Region Wise Quantity")
    fig4 = px.pie(donut_df, values="Quantity_Sold", names="Region", hole=0.5)
    fig4.update_traces(textposition='outside')
    fig4.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig4, use_container_width=True)

    with st.expander("View Data"):
        st.dataframe(donut_df)
    st.download_button("Download", donut_df.to_csv(index=False), "region_qty.csv")

st.divider()

# -------------------------------
# Inward & Dispatch
# -------------------------------
c3, c4 = st.columns(2)

with c3:
    st.subheader("📦 Inward Date Sales Trend (Brand-wise)")
    filtered_df["Inward_Date"] = pd.to_datetime(filtered_df["Inward_Date"])
    inward = filtered_df.groupby([filtered_df["Inward_Date"].dt.to_period("M"), "Brand"])["Sales"].sum().reset_index()
    inward["Inward_Date"] = inward["Inward_Date"].astype(str)

    fig5 = px.line(inward, x="Inward_Date", y="Sales", color="Brand", markers=True)
    fig5.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig5, use_container_width=True)

    with st.expander("View Data"):
        st.dataframe(inward)
    st.download_button("Download", inward.to_csv(index=False), "inward.csv")

with c4:
    st.subheader("🚚 Dispatch Date Sales Trend (Brand-wise)")
    filtered_df["Dispatch_Date"] = pd.to_datetime(filtered_df["Dispatch_Date"])
    dispatch = filtered_df.groupby([filtered_df["Dispatch_Date"].dt.to_period("M"), "Brand"])["Sales"].sum().reset_index()
    dispatch["Dispatch_Date"] = dispatch["Dispatch_Date"].astype(str)

    fig6 = px.line(dispatch, x="Dispatch_Date", y="Sales", color="Brand", markers=True)
    fig6.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig6, use_container_width=True)

    with st.expander("View Data"):
        st.dataframe(dispatch)
    st.download_button("Download", dispatch.to_csv(index=False), "dispatch.csv")

st.divider()

# -------------------------------
# Core & Processor
# -------------------------------
col_1, col_2 = st.columns(2)

with col_1:
    st.subheader("💻 Core Specification Sales")
    core_df = filtered_df.groupby("Core_Specification")["Sales"].sum().reset_index()
    core_df["label"] = core_df["Sales"].apply(format_number)

    fig7 = px.bar(core_df, x="Core_Specification", y="Sales", text="label")
    fig7.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig7, use_container_width=True)

    with st.expander("View Data"):
        st.dataframe(core_df)
    st.download_button("Download", core_df.to_csv(index=False), "core.csv")

with col_2:
    st.subheader("⚙️ Processor Specification Sales")
    proc_df = filtered_df.groupby("Processor_Specification")["Sales"].sum().reset_index()
    proc_df["label"] = proc_df["Sales"].apply(format_number)

    fig8 = px.bar(proc_df, x="Processor_Specification", y="Sales", text="label")
    fig8.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig8, use_container_width=True)

    with st.expander("View Data"):
        st.dataframe(proc_df)
    st.download_button("Download", proc_df.to_csv(index=False), "processor.csv")

st.divider()

# -------------------------------
# Footer
# -------------------------------
st.markdown("### ✅ Developed using Python & Streamlit")
