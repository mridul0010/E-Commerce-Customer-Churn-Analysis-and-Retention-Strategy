import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="E-Commerce Churn Analysis", page_icon="📊", layout="wide")

# ── Load & Prepare Data ──────────────────────────────────────────────────────

@st.cache_data
def load_data():

    # Google Drive direct download link
    url = "https://drive.google.com/uc?id=1cVtj9L1CpqWACu1KCp-UCYo3NpR8RVKU"

    df = pd.read_csv(url)

    df["Purchase Date"] = pd.to_datetime(df["Purchase Date"], format="mixed")

    df["Age Group"] = pd.cut(
        df["Customer Age"],
        bins=[1, 17, 25, 40, 60, 100],
        labels=["1-17", "18-25", "26-40", "41-60", "60+"],
    )

    return df

df = load_data()

# ── Sidebar Filters ──────────────────────────────────────────────────────────

st.sidebar.title("🔍 Filters")

selected_categories = st.sidebar.multiselect(
    "Product Category", df["Product Category"].unique(), default=df["Product Category"].unique()
)
selected_genders = st.sidebar.multiselect(
    "Gender", df["Gender"].unique(), default=df["Gender"].unique()
)
selected_age_groups = st.sidebar.multiselect(
    "Age Group", df["Age Group"].cat.categories.tolist(), default=df["Age Group"].cat.categories.tolist()
)
selected_payment = st.sidebar.multiselect(
    "Payment Method", df["Payment Method"].unique(), default=df["Payment Method"].unique()
)

filtered = df[
    (df["Product Category"].isin(selected_categories))
    & (df["Gender"].isin(selected_genders))
    & (df["Age Group"].isin(selected_age_groups))
    & (df["Payment Method"].isin(selected_payment))
]

# ── Header ────────────────────────────────────────────────────────────────────

st.title("📊 E-Commerce Customer Churn Dashboard")

total_customers = filtered["Customer Name"].nunique()
total_revenue = filtered["Total Purchase Amount"].sum()
churn_rate = filtered["Churn"].mean() * 100
revenue_lost = filtered[filtered["Churn"] == 1]["Total Purchase Amount"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", f"{total_customers:,}")
col2.metric("Total Revenue", f"${total_revenue:,.0f}")
col3.metric("Churn Rate", f"{churn_rate:.1f}%")
col4.metric("Revenue Lost to Churn", f"${revenue_lost:,.0f}")

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Data Overview & Feature Distribution", "🏢 Business Analysis", "🧠 Customer Behavior",
    "💰 Revenue Impact", "📋 Strategy & Insights"
])

# ── Tab 1: Data Overview & Feature Distribution Analysis ───────────────────────────────────────────────

with tab1:
    st.subheader("Data Overview & Feature Distribution Analysis")

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(
            filtered["Product Category"].value_counts().reset_index(),
            x="Product Category", y="count", color="Product Category",
            title="Product Category Distribution",
        )
        st.plotly_chart(fig, width='stretch')

    with c2:
        fig = px.histogram(
            filtered, x="Product Price", nbins=40, title="Product Price Distribution",
            marginal="box",
        )
        st.plotly_chart(fig, width='stretch')

    c3, c4 = st.columns(2)

    with c3:
        fig = px.bar(
            filtered["Payment Method"].value_counts().reset_index(),
            x="Payment Method", y="count", color="Payment Method",
            title="Payment Method Distribution",
        )
        st.plotly_chart(fig, width='stretch')

    with c4:
        fig = px.bar(
            filtered["Gender"].value_counts().reset_index(),
            x="Gender", y="count", color="Gender",
            title="Gender Distribution",
        )
        st.plotly_chart(fig, width='stretch')

    c5, c6 = st.columns(2)

    with c5:
        churn_counts = filtered["Churn"].value_counts().reset_index()
        churn_counts["Churn"] = churn_counts["Churn"].map({0: "Retained", 1: "Churned"})
        fig = px.bar(churn_counts, x="Churn", y="count", color="Churn", title="Churn Distribution")
        st.plotly_chart(fig, width='stretch')

    with c6:
        fig = px.bar(
            filtered["Age Group"].value_counts().sort_index().reset_index(),
            x="Age Group", y="count", color="Age Group",
            title="Age Group Distribution",
        )
        st.plotly_chart(fig, width='stretch')

# ── Tab 2: Business Analysis ─────────────────────────────────────────────────

with tab2:
    st.subheader("Business Analysis — Churn Drivers")

    # Churn by Product Category
    product_churn = filtered.groupby("Product Category")["Churn"].value_counts().reset_index()
    product_churn["Churn"] = product_churn["Churn"].map({0: "Retained", 1: "Churned"})
    fig = px.bar(
        product_churn, x="Product Category", y="count", color="Churn",
        barmode="group", title="Customer Churn by Product Category",
    )
    st.plotly_chart(fig, width='stretch')

    with st.expander("💡 Insight"):
        st.markdown("""
        - **Books** and **Clothing** have the highest number of churned customers.
        - Retained customers are high across all categories, but Books and Clothing still lose the most customers.
        """)

    c1, c2 = st.columns(2)

    with c1:
        # Churn by Age Group
        age_churn = filtered.groupby("Age Group", observed=True)["Churn"].value_counts().reset_index()
        age_churn["Churn"] = age_churn["Churn"].map({0: "Retained", 1: "Churned"})
        fig = px.bar(
            age_churn, x="Age Group", y="count", color="Churn",
            barmode="group", title="Customer Churn by Age Group",
        )
        st.plotly_chart(fig, width='stretch')

        with st.expander("💡 Insight"):
            st.markdown("""
            - Older customers (41–60, 60+) show slightly higher churn risk.
            - 18–25 customers have relatively better retention.
            """)

    with c2:
        # Churn by Gender
        gender_churn = filtered.groupby("Gender")["Churn"].value_counts().reset_index()
        gender_churn["Churn"] = gender_churn["Churn"].map({0: "Retained", 1: "Churned"})
        fig = px.bar(
            gender_churn, x="Gender", y="count", color="Churn",
            barmode="group", title="Customer Churn by Gender",
        )
        st.plotly_chart(fig, width='stretch')

        with st.expander("💡 Insight"):
            st.markdown("Gender does not appear to be a strong factor influencing customer churn.")

    c3, c4 = st.columns(2)

    with c3:
        # Average Purchase Value — Churned vs Retained
        avg_purchase = (
            filtered.groupby("Churn")["Total Purchase Amount"].mean().reset_index()
        )
        avg_purchase["Churn"] = avg_purchase["Churn"].map({0: "Retained", 1: "Churned"})
        fig = px.bar(
            avg_purchase, x="Churn", y="Total Purchase Amount", color="Churn",
            title="Avg Purchase Value — Churned vs Retained",
        )
        st.plotly_chart(fig, width='stretch')

        with st.expander("💡 Insight"):
            st.markdown("""
            - Churned customers have a slightly higher average purchase value.
            - High-value customers are also leaving — churn is likely caused by experience issues, not spending power.
            """)

    with c4:
        # Churn by Returns
        return_churn = filtered.groupby("Returns")["Churn"].value_counts().reset_index()
        return_churn["Churn"] = return_churn["Churn"].map({0: "Retained", 1: "Churned"})
        return_churn["Returns"] = return_churn["Returns"].map({0: "No Return", 1: "Returned"})
        fig = px.bar(
            return_churn, x="Returns", y="count", color="Churn",
            barmode="group", title="Customer Churn by Returns",
        )
        st.plotly_chart(fig, width='stretch')

        with st.expander("💡 Insight"):
            st.markdown("Product returns do not strongly influence customer churn in this dataset.")

    # Churn by Payment Method
    payment_churn = filtered.groupby("Payment Method")["Churn"].value_counts().reset_index()
    payment_churn["Churn"] = payment_churn["Churn"].map({0: "Retained", 1: "Churned"})
    fig = px.bar(
        payment_churn, x="Payment Method", y="count", color="Churn",
        barmode="group", title="Impact of Payment Method on Customer Churn",
    )
    st.plotly_chart(fig, width='stretch')

    churn_rate_payment = round(
        filtered.groupby("Payment Method")["Churn"].mean() * 100, 2
    ).reset_index()
    churn_rate_payment.columns = ["Payment Method", "Churn Rate (%)"]
    fig = px.bar(
        churn_rate_payment, x="Payment Method", y="Churn Rate (%)",
        color="Payment Method", title="Churn Rate (%) by Payment Method",
    )
    st.plotly_chart(fig, width='stretch')

    with st.expander("💡 Insight"):
        st.markdown("""
        - **Credit Card** users have the highest churn rate.
        - **Crypto** users have the lowest churn rate.
        """)

# ── Tab 3: Customer Behavior ─────────────────────────────────────────────────

with tab3:
    st.subheader("Customer Behavior Analysis")

    c1, c2 = st.columns(2)

    with c1:
        # Churn by Price Range
        temp = filtered.copy()
        temp["price_range"] = pd.qcut(temp["Product Price"], q=5, duplicates="drop").astype(str)
        price_churn = temp.groupby("price_range", observed=True)["Churn"].mean().reset_index()
        price_churn["Churn"] = round(price_churn["Churn"] * 100, 2)
        fig = px.bar(
            price_churn, x="price_range", y="Churn",
            title="Churn Rate (%) by Price Range",
            labels={"Churn": "Churn Rate (%)", "price_range": "Price Range"},
        )
        st.plotly_chart(fig, width='stretch')

        with st.expander("💡 Insight"):
            st.markdown("Churn rate is similar across price ranges — product price does not strongly influence churn.")

    with c2:
        # Churn by Spending Segment
        spending = filtered.groupby("Customer Name").agg(
            {"Total Purchase Amount": "sum", "Churn": "max"}
        ).reset_index()
        spending["Spending Segment"] = pd.qcut(
            spending["Total Purchase Amount"], q=3, labels=["Low", "Medium", "High"]
        )
        seg_churn = spending.groupby("Spending Segment", observed=False)["Churn"].mean().reset_index()
        seg_churn["Churn"] = round(seg_churn["Churn"] * 100, 2)
        fig = px.bar(
            seg_churn, x="Spending Segment", y="Churn",
            title="Churn Rate (%) by Spending Segment",
            labels={"Churn": "Churn Rate (%)"},
            color="Spending Segment",
        )
        st.plotly_chart(fig, width='stretch')

        with st.expander("💡 Insight"):
            st.markdown("""
            - **High-spending customers churn significantly more** than low or medium spenders.
            - Companies should focus retention strategies on high-value customers.
            """)

    c3, c4 = st.columns(2)

    with c3:
        # Churn by Number of Categories Purchased
        cat_count = filtered.groupby("Customer Name").agg(
            {"Product Category": "nunique", "Churn": "max"}
        ).rename(columns={"Product Category": "Category Count"})
        cat_churn = cat_count.groupby("Category Count")["Churn"].mean().reset_index()
        cat_churn["Churn"] = round(cat_churn["Churn"] * 100, 2)
        fig = px.bar(
            cat_churn, x="Category Count", y="Churn",
            title="Churn Rate (%) by Number of Categories Purchased",
            labels={"Churn": "Churn Rate (%)"},
        )
        st.plotly_chart(fig, width='stretch')

        with st.expander("💡 Insight"):
            st.markdown("""
            - Churn increases as customers purchase from more categories.
            - Multi-category buyers may be exploratory shoppers rather than loyal users.
            """)

    with c4:
        # Churn by Quantity
        qty_churn = filtered.groupby("Quantity")["Churn"].mean().reset_index()
        qty_churn["Churn"] = round(qty_churn["Churn"] * 100, 2)
        fig = px.bar(
            qty_churn, x="Quantity", y="Churn",
            title="Churn Rate (%) by Quantity per Order",
            labels={"Churn": "Churn Rate (%)"},
        )
        st.plotly_chart(fig, width='stretch')

        with st.expander("💡 Insight"):
            st.markdown("Purchase quantity does not strongly affect churn.")

    # Single-item buyers
    st.markdown("---")
    st.subheader("Single-Item Buyers — Churn by Purchase Size")
    single = filtered[filtered["Quantity"] == 1].copy()
    if len(single) > 0:
        single["Purchase Segment"] = pd.qcut(
            single["Total Purchase Amount"], q=3, labels=["Small", "Medium", "Large"], duplicates="drop"
        )
        single_churn = single.groupby("Purchase Segment", observed=False)["Churn"].mean().reset_index()
        single_churn["Churn"] = round(single_churn["Churn"] * 100, 2)
        fig = px.bar(
            single_churn, x="Purchase Segment", y="Churn",
            title="Churn Rate (%) by Purchase Size (Single-Item Buyers)",
            labels={"Churn": "Churn Rate (%)"},
            color="Purchase Segment",
        )
        st.plotly_chart(fig, width='stretch')

        with st.expander("💡 Insight"):
            st.markdown("""
            - Single-item buyers churn at nearly identical rates regardless of item price.
            - Companies should not assume high-value single-purchase customers are loyal.
            """)

# ── Tab 4: Revenue Impact ────────────────────────────────────────────────────

with tab4:
    st.subheader("Revenue Impact Analysis")

    total_rev = filtered["Total Purchase Amount"].sum()
    churn_rev = filtered[filtered["Churn"] == 1]["Total Purchase Amount"].sum()
    pct_lost = round(churn_rev / total_rev * 100, 2) if total_rev > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Revenue", f"${total_rev:,.0f}")
    m2.metric("Revenue Lost to Churn", f"${churn_rev:,.0f}")
    m3.metric("% Revenue Lost", f"{pct_lost}%")

    st.markdown("> Customers who churned contributed **{:.1f}%** of total revenue.".format(pct_lost))

    cat_rev = (
        filtered[filtered["Churn"] == 1]
        .groupby("Product Category")["Total Purchase Amount"]
        .sum()
        .reset_index()
    )
    fig = px.bar(
        cat_rev, x="Product Category", y="Total Purchase Amount",
        color="Product Category",
        title="Revenue Lost Due to Customer Churn by Product Category",
        labels={"Total Purchase Amount": "Revenue Lost ($)"},
    )
    st.plotly_chart(fig, width='stretch')

    with st.expander("💡 Insight"):
        st.markdown("""
        - **Books** and **Clothing** categories have the highest churn-related revenue loss.
        - This indicates poor retention among high-value buyers in these categories.
        """)

# ── Tab 5: Strategy & Insights ───────────────────────────────────────────────

with tab5:
    st.subheader("Customer Retention Strategy Based on Churn Analysis")

    st.markdown("### 1. Which Customers Should Be Targeted for Retention Campaigns?")
    st.markdown("""
    Based on the analysis, the highest-risk and highest-impact churn segments are:
    - **High-spending customers** — churn rate ~34%
    - **Customers buying from multiple product categories** — exploratory shoppers
    - **Customers purchasing Books and Clothing** — largest revenue loss
    - **Credit card users** — largest share of churn by payment method
    """)

    st.markdown("### 2. What Incentives Would Reduce Churn?")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **🎁 Personalized Discounts**
        - 10% off next purchase
        - Limited-time personalized coupons

        **📦 Free & Easy Returns**
        - Builds customer trust
        - Improves shopping experience
        """)
    with col2:
        st.markdown("""
        **⭐ Loyalty Programs**
        - Reward points & cashback
        - Tier-based membership

        **🎯 Product Recommendations**
        - Based on previous purchases
        - Frequently bought items
        """)

    st.markdown("### 3. Which Segment Should Receive Personalized Marketing?")
    st.markdown("""
    **High-Spending Customers** — they have the highest churn rate, revenue contribution,
    and lifetime value. Treat them as VIP segments with:
    - Exclusive offers & early access to deals
    - Premium customer support
    - Personalized product suggestions
    """)

    st.markdown("---")
    st.info("""
    **Key Takeaway:** Customer *behavior* is a stronger predictor of churn than demographics.
    Gender has minimal effect, age has moderate effect, but purchase behavior has the strongest effect.
    """)


