import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ----------------------
# Page Configuration & Styling
# ----------------------
st.set_page_config(
    layout="wide", 
    page_title="Marketing Intelligence Dashboard",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS styling with brown-beige theme
st.markdown("""
<style>
    /* Global styling */
    .main > div {
        padding-top: 1rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    
    /* Compact dashboard header */
    .dashboard-header {
        background: linear-gradient(135deg, #8D6E63 0%, #A1887F 100%);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 16px rgba(141, 110, 99, 0.3);
    }
    
    .dashboard-title {
        font-size: 1.8rem;
        font-weight: 600;
        margin: 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .dashboard-subtitle {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0.25rem 0 0 0;
    }
    
    /* Compact KPI Cards */
    .kpi-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    .kpi-card {
        background: linear-gradient(145deg, #F5F5DC 0%, #EFEBE9 100%);
        border: 1px solid #8D6E63;
        border-radius: 8px;
        padding: 0.75rem;
        width: 120px;
        height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 2px 8px rgba(141, 110, 99, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .kpi-value {
        font-size: 0.9rem;
        font-weight: 700;
        color: #5D4037;
        margin: 0;
        text-align: center;
    }

    .kpi-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #8D6E63;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        text-align: center;
        line-height: 1.1;
    }
        
    .kpi-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(141, 110, 99, 0.3);
    }
    
    .kpi-value.positive {
        color: #6D4C41;
    }
    
    .kpi-value.metric {
        color: #8D6E63;
    }
    
    /* Chart Title Styling */
    .chart-title {
        font-size: 1rem;
        font-weight: 600;
        color: #5D4037;
        margin-bottom: 0.5rem;
        padding-bottom: 0.25rem;
        border-bottom: 2px solid #D7CCC8;
    }
    
    /* Compact filter section */
    .filter-container {
        background: linear-gradient(145deg, #EFEBE9 0%, #E8E2E2 100%);
        border: 1px solid #D7CCC8;
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(141, 110, 99, 0.1);
    }
    
    /* Inline filters */
    .filter-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .filter-item {
        display: flex;
        flex-direction: column;
        min-width: 150px;
    }
    
    .filter-item label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #5D4037;
        margin-bottom: 0.25rem;
    }
    
    /* Compact metrics section */
    .metrics-section {
        background: linear-gradient(135deg, #F3E5AB 0%, #EDC967 100%);
        border: 1px solid #D7CCC8;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(141, 110, 99, 0.15);
    }
    
    /* Grid layouts */
    .main-grid {
        display: grid;
        grid-template-columns: 300px 1fr;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .charts-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .insights-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Streamlit widget styling */
    .stSelectbox > div > div > div {
        background-color: #F5F5DC;
        border: 1px solid #D7CCC8;
    }
    
    .stMultiSelect > div > div > div {
        background-color: #F5F5DC;
        border: 1px solid #D7CCC8;
    }
    
    .stDateInput > div > div > input {
        background-color: #F5F5DC;
        border: 1px solid #D7CCC8;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------
# Utility Functions
# ----------------------
def aggregate(df, freq):
    """Aggregate metrics by given frequency (D=Day, W=Week, M=Month)."""
    if df.empty:
        return df
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.groupby("date").sum(numeric_only=True).reset_index()
    df = df.set_index("date").resample(freq).sum().reset_index()
    return df

def total_metric(df, column):
    return df[column].sum() if column in df.columns else 0

def create_kpi_card(label, value, is_currency=False, is_positive=False, is_metric=False):
    """Create a compact KPI card with brown-beige styling."""
    value_class = "positive" if is_positive else ("metric" if is_metric else "")
    
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {value_class}">{value}</div>
    </div>
    """

def style_figure(fig):
    """Applies the brown-beige theme to a Plotly figure."""
    fig.update_layout(
        plot_bgcolor='rgba(245,245,220,0.3)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=40),
        font=dict(family="Inter, sans-serif", size=10, color="#5D4037"),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#F5F5DC",
            bordercolor="#D7CCC8",
            font=dict(color="#5D4037")
        ),
        height=230, # Set a fixed height to maintain layout consistency
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9)
        )
    )
    fig.update_xaxes(
        gridcolor="#E8DCC6",
        linecolor="#D7CCC8",
        tickcolor="#D7CCC8",
        tickfont=dict(size=9)
    )
    fig.update_yaxes(
        gridcolor="#E8DCC6",
        linecolor="#D7CCC8",
        tickcolor="#D7CCC8",
        tickfont=dict(size=9)
    )
    return fig

# ----------------------
# Load Data
# ----------------------
@st.cache_data
def load_data():
    try:
        google_df = pd.read_csv("Google.csv")
        facebook_df = pd.read_csv("Facebook.csv")
        tiktok_df = pd.read_csv("TikTok.csv")
        business_df = pd.read_csv("Business.csv")
        
        for df in [google_df, facebook_df, tiktok_df, business_df]:
            df["date"] = pd.to_datetime(df["date"])
        
        google_df["platform"] = "Google"
        facebook_df["platform"] = "Facebook"
        tiktok_df["platform"] = "TikTok"
        
        return google_df, facebook_df, tiktok_df, business_df
    except FileNotFoundError:
        st.error("Data files not found. Please ensure all CSV files are in the correct directory.")
        return None, None, None, None

google_df, facebook_df, tiktok_df, business_df = load_data()

if google_df is None:
    st.stop()

# ----------------------
# Compact Dashboard Header
# ----------------------
st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">📊 Marketing Intelligence Dashboard</h1>
    <p class="dashboard-subtitle">Real-time insights for data-driven marketing decisions</p>
</div>
""", unsafe_allow_html=True)

# ----------------------
# Compact Inline Filters Section
# ----------------------
st.markdown('<div class="filter-container">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1.5])

with col1:
    min_date = max(df["date"].min() for df in [google_df, facebook_df, tiktok_df, business_df])
    max_date = min(df["date"].max() for df in [google_df, facebook_df, tiktok_df, business_df])
    default_start = max_date - timedelta(days=30)
    date_range = st.date_input(
        "📅 Date Range", [default_start, max_date], min_value=min_date, max_value=max_date
    )

with col2:
    platforms_selected = st.multiselect(
        "🚀 Platforms", ["Google", "Facebook", "TikTok"], default=["Google", "Facebook", "TikTok"]
    )

with col3:
    freq_option = st.selectbox("📊 Frequency", ["Day", "Week", "Month"], index=1)
    freq_map = {"Day": "D", "Week": "W", "Month": "M"}
    freq = freq_map[freq_option]

with col4:
    all_states = pd.concat([google_df, facebook_df, tiktok_df])["state"].unique().tolist()
    states_selected = st.multiselect(
        "🌍 Regions", options=all_states, default=all_states[:3] if len(all_states) > 3 else all_states
    )

st.markdown('</div>', unsafe_allow_html=True)

# ----------------------
# Data Processing
# ----------------------
platform_dfs = []
if "Google" in platforms_selected and google_df is not None: platform_dfs.append(google_df)
if "Facebook" in platforms_selected and facebook_df is not None: platform_dfs.append(facebook_df)
if "TikTok" in platforms_selected and tiktok_df is not None: platform_dfs.append(tiktok_df)

combined_platforms = pd.concat(platform_dfs, ignore_index=True) if platform_dfs else pd.DataFrame()

if not combined_platforms.empty:
    combined_platforms = combined_platforms[
        (combined_platforms["state"].isin(states_selected)) &
        (combined_platforms["date"] >= pd.to_datetime(date_range[0])) &
        (combined_platforms["date"] <= pd.to_datetime(date_range[1]))
    ]

business_filtered = business_df[
    (business_df["date"] >= pd.to_datetime(date_range[0])) &
    (business_df["date"] <= pd.to_datetime(date_range[1]))
]

agg_platforms = aggregate(combined_platforms, freq)
agg_business = aggregate(business_filtered, freq)

# ----------------------
# Calculate KPIs
# ----------------------
total_spend = total_metric(combined_platforms, "spend")
attributed_revenue = total_metric(combined_platforms, "attributed revenue")
new_orders = total_metric(business_filtered, "# of new orders")
new_customers = total_metric(business_filtered, "new customers")
gross_profit = total_metric(business_filtered, "gross profit")
total_revenue = total_metric(business_filtered, "total revenue")

roas = (attributed_revenue / total_spend) if total_spend > 0 else 0
cac = (total_spend / new_customers) if new_customers > 0 else 0
conversion_rate = (new_orders / new_customers * 100) if new_customers > 0 else 0
profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

# ----------------------
# Main Layout: KPIs + Main Chart
# ----------------------
main_col1, main_col2 = st.columns([1, 2])

with main_col1:
    st.markdown("### 📈 **KPIs**")
    kpi_data = [
        ("Marketing Spend", f"${total_spend:,.0f}"), ("Revenue", f"${attributed_revenue:,.0f}"),
        ("ROAS", f"{roas:.2f}x"), ("CAC", f"${cac:.0f}"),
        ("Orders", f"{new_orders:,}"), ("Customers", f"{new_customers:,}"),
        ("Profit", f"${gross_profit:,.0f}"), ("Margin", f"{profit_margin:.1f}%")
    ]
    for i in range(0, len(kpi_data), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(kpi_data):
                label, value = kpi_data[i + j]
                is_positive = label in ["Revenue", "ROAS", "Profit", "Margin"]
                col.markdown(create_kpi_card(label, value, is_positive=is_positive), unsafe_allow_html=True)

with main_col2:
    if not agg_business.empty and not agg_platforms.empty:
        line_df = pd.DataFrame({"date": agg_business["date"]})
        line_df["Marketing Spend"] = agg_platforms["spend"].values if len(agg_platforms) > 0 else 0
        line_df["Attributed Revenue"] = agg_platforms["attributed revenue"].values if len(agg_platforms) > 0 else 0
        line_df["Total Business Revenue"] = agg_business["total revenue"].values
        
        fig_line = go.Figure()
        colors = ['#8D6E63', '#A1887F', '#BCAAA4']
        metrics = ["Marketing Spend", "Attributed Revenue", "Total Business Revenue"]
        
        for i, metric in enumerate(metrics):
            fig_line.add_trace(go.Scatter(
                x=line_df["date"], y=line_df[metric], mode='lines+markers', name=metric,
                line=dict(color=colors[i], width=2), marker=dict(size=6)
            ))
        
        with st.container(border=True):
            st.markdown('<div class="chart-title">📈 Performance Trends</div>', unsafe_allow_html=True)
            fig_line = style_figure(fig_line)
            st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})

# ----------------------
# Secondary Charts Row
# ----------------------
chart_col1, chart_col2 = st.columns([1, 1])

with chart_col1:
    if not combined_platforms.empty:
        summary = combined_platforms.groupby("platform").agg(
            {"spend": "sum", "attributed revenue": "sum"}
        ).reset_index()
        summary['ROAS'] = summary['attributed revenue'] / summary['spend']
        
        fig_platform = go.Figure(data=[
            go.Bar(name="Spend", x=summary["platform"], y=summary["spend"], marker_color='#8D6E63'),
            go.Bar(name="Revenue", x=summary["platform"], y=summary["attributed revenue"], marker_color='#A1887F')
        ])
        
        with st.container(border=True):
            st.markdown('<div class="chart-title">🚀 Platform Performance</div>', unsafe_allow_html=True)
            fig_platform = style_figure(fig_platform)
            fig_platform.update_layout(barmode="group")
            st.plotly_chart(fig_platform, use_container_width=True, config={'displayModeBar': False})

with chart_col2:
    if not combined_platforms.empty and 'campaign' in combined_platforms.columns:
        campaigns_df = combined_platforms.groupby("campaign")[["spend", "attributed revenue"]].sum()
        campaigns_df['ROAS'] = campaigns_df['attributed revenue'] / campaigns_df['spend']
        campaigns_df = campaigns_df.sort_values("spend", ascending=False).head(6).reset_index()
        
        fig_campaigns = go.Figure(data=[
            go.Bar(name="Spend", x=campaigns_df["campaign"], y=campaigns_df["spend"], marker_color='#BCAAA4'),
            go.Bar(name="Revenue", x=campaigns_df["campaign"], y=campaigns_df["attributed revenue"], marker_color='#D7CCC8')
        ])
        
        with st.container(border=True):
            st.markdown('<div class="chart-title">🏆 Top Campaigns</div>', unsafe_allow_html=True)
            fig_campaigns = style_figure(fig_campaigns)
            fig_campaigns.update_layout(barmode="group", xaxis={'tickangle': -45})
            st.plotly_chart(fig_campaigns, use_container_width=True, config={'displayModeBar': False})

# ----------------------
# Bottom Insights Row
# ----------------------
if not business_filtered.empty:
    insight_col1, insight_col2 = st.columns([1, 1])
    
    with insight_col1:
        if not agg_business.empty:
            revenue_df = agg_business[['date', 'total revenue', 'gross profit']].copy()
            
            fig_revenue = go.Figure(data=[
                go.Scatter(
                    x=revenue_df['date'], y=revenue_df['total revenue'], fill='tonexty',
                    mode='lines', name='Total Revenue', line=dict(color='#8D6E63')
                ),
                go.Scatter(
                    x=revenue_df['date'], y=revenue_df['gross profit'], fill='tozeroy',
                    mode='lines', name='Gross Profit', line=dict(color='#A1887F')
                )
            ])
            with st.container(border=True):
                st.markdown('<div class="chart-title">💰 Revenue vs Profit</div>', unsafe_allow_html=True)
                fig_revenue = style_figure(fig_revenue)
                st.plotly_chart(fig_revenue, use_container_width=True, config={'displayModeBar': False})
    
    with insight_col2:
        if not agg_business.empty:
            customer_df = agg_business[['date', 'new customers', '# of new orders']].copy()
            
            fig_customers = go.Figure()
            fig_customers.add_trace(go.Scatter(
                x=customer_df['date'], y=customer_df['new customers'], mode='lines+markers',
                name='New Customers', line=dict(color='#8D6E63', width=2), yaxis='y'
            ))
            fig_customers.add_trace(go.Scatter(
                x=customer_df['date'], y=customer_df['# of new orders'], mode='lines+markers',
                name='New Orders', line=dict(color='#A1887F', width=2), yaxis='y2'
            ))
            
            with st.container(border=True):
                st.markdown('<div class="chart-title">👥 Customer Trends</div>', unsafe_allow_html=True)
                fig_customers = style_figure(fig_customers)
                fig_customers.update_layout(
                    yaxis2=dict(title="New Orders", overlaying='y', side='right'),
                    yaxis=dict(title="New Customers"),
                    legend=dict(x=0, y=1.2) # Adjust legend to not overlap title
                )
                st.plotly_chart(fig_customers, use_container_width=True, config={'displayModeBar': False})