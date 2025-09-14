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
    page_title="Dashboard",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS styling with brown-beige theme
st.markdown("""
<style>
    /* Global styling */
    .main > div {
        padding-top: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    
    /* Compact dashboard header */
        .dashboard-title {
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        color: white;
        margin: 3px 115px 3px 0px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    .dashboard-header {
        background: linear-gradient(135deg, #4A90E2 0%, #50E3C2 100%);
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(74, 144, 226, 0.3);
        padding: 1rem 1rem 1rem 1rem;
        margin-bottom: 1rem;
    }
    
        
    /* Compact KPI Cards */
    .kpi-container {
        display: flex;
        flex-direction: row;
        gap: 0.5px;
    }
    .kpi-card {
        background: linear-gradient(145deg, #E0F7FA 0%, #B2EBF2 100%);
        border: 1px solid #4A90E2;
        border-radius: 8px;
        padding: 1rem;
        width: 190px;
        height: 75px;
        display: flex;
        flex-direction: column;
        justify-content: space-evenly;
        align-items: center;
        box-shadow: 0 2px 8px rgba(74, 144, 226, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .kpi-value {
        font-size: 0.9rem;
        font-weight: 700;
        color: rgb(0,69,121);
        margin: 0;
        text-align: center;
    }

    .kpi-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: rgb(0,69,121);
        margin:0;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        text-align: center;
        line-height: 1.1;
    }
        
    .kpi-card:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 14px rgba(74, 144, 226, 0.3);
    }
    
    .kpi-value.positive {
        color: rgb(4,121,0);
    }
    
    .kpi-value.metric {
        color: rgb(0,69,121);
    }
    
    /* Chart Title Styling */
    .chart-title {
        font-size: 1rem;
        font-weight: 600;
        color: rgb(0,46,121);
        margin-bottom: 0.5rem;
        padding-bottom: 0.25rem;
        border-bottom: 2px solid rgb(0,46,121);
    }
    
    /* Compact filter section */
    .filter-container {
        background: linear-gradient(145deg, #E0F2F1 0%, #B2DFDB 100%);
        border: 1px solid #80CBC4;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(74, 144, 226, 0.1);
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


    /* Targets the main container of the dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #4A90E2 !important;
        border-radius: 8px !important;
    }

    /* Styles the header row */
    [data-testid="stDataFrame"] thead th {
        background-color: #B2EBF2 !important;
        color: #004D40 !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.8rem;
        text-align: center;
    }


    .filter-item label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #004D40;
        margin-bottom: 0.25rem;
    }
    
    /* Compact metrics section */
    .metrics-section {
        background: linear-gradient(135deg, #FFF9C4 0%, #FFE57F 100%);
        border: 1px solid #FFD54F;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(255, 193, 7, 0.15);
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
        background-color: rgb(242,224,250);
        border: 1px solid #80CBC4;
    }
    
    .stMultiSelect > div > div > div {
        background-color: rgb(242,224,250);
        border: 1px solid #80CBC4;
    }
    
    .stDateInput > div > div > input {
        background-color: rgb(242,224,250);
        border: 1px solid #80CBC4;
    }
    .stDateInput > div > div {
    background-color: rgb(242,224,250) !important;
    border: 1px solid #80CBC4 !important;
    border-radius: 4px;
}    
    

    .stApp {
    background-color:#E2D5F7 !important; 
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
        height=360, # Set a fixed height to maintain layout consistency
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

col1, col2 = st.columns([2, 5])
with col1:
    st.markdown(
        '<div class="dashboard-header"><div class="dashboard-title">E-commerce Dashboard</div></div>',
        unsafe_allow_html=True,
    )

with col2:
    colf1, colf2, colf3, colf4 = st.columns([1.4, 1.1, 1, 1.2])
    with colf1:
        min_date = max(df["date"].min() for df in [google_df, facebook_df, tiktok_df, business_df])
        max_date = min(df["date"].max() for df in [google_df, facebook_df, tiktok_df, business_df])
        default_start = max_date - timedelta(days=30)
        date_range = st.date_input(
            "Date Range", [default_start, max_date], min_value=min_date, max_value=max_date
        )
    with colf2:
        platforms_selected = st.multiselect(
            " Platforms", ["Google", "Facebook", "TikTok"], default=["Google", "Facebook", "TikTok"]
        )
    with colf3:
        freq_option = st.selectbox(" Frequency", ["Day", "Week", "Month"], index=1)
        freq_map = {"Day": "D", "Week": "W", "Month": "M"}
        freq = freq_map[freq_option]
    with colf4:
        all_states = pd.concat([google_df, facebook_df, tiktok_df])["state"].unique().tolist()
        states_selected = st.multiselect(
            "🌍 Regions", options=all_states, default=all_states[:3] if len(all_states) > 3 else all_states
        )

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

# NEW: Create a unified DataFrame by merging aggregated data
merged_df = pd.DataFrame() # Create an empty df to avoid errors if one is empty
if not agg_business.empty:
    merged_df = agg_business.copy()
    if not agg_platforms.empty:
        merged_df = pd.merge(agg_business, agg_platforms, on='date', how='left')

# Fill any missing marketing data with 0 (for days with no spend)
merged_df.fillna(0, inplace=True)

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
mer = (total_revenue / total_spend) if total_spend > 0 else 0
total_clicks = total_metric(combined_platforms, "clicks")
total_impressions = total_metric(combined_platforms, "impression")
ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
total_orders = total_metric(business_filtered, "# of orders")
aov = (total_revenue / total_orders) if total_orders > 0 else 0
cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
poas = (gross_profit / total_spend) if total_spend > 0 else 0
# ----------------------
# Main Layout: KPIs + Main Chart
# ----------------------
main_col1, main_col2 = st.columns([1, 2])

with main_col1:
    kpi_data = [
        ("Total Marketing Spend", f"${total_spend:,.0f}"), ("Attributed Revenue", f"${attributed_revenue:,.0f}"),
        ("ROAS", f"{roas:.2f}x"), ("Customer Acquisition Cost (CAC)", f"${cac:.0f}"),
        ("New Orders", f"{new_orders:,}"), ("New Customers", f"{new_customers:,}"),
        ("Gross Profit", f"${gross_profit:,.0f}"), ("Profit Margin", f"{profit_margin:.1f}%"),
        ("Marketing Efficiency Ratio", f"{mer:.2f}x"),("Click-Through Rate (CTR)", f"{ctr:.2f}x")

    ]
    for i in range(0, len(kpi_data), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(kpi_data):
                label, value = kpi_data[i + j]
                is_positive = label in ["Attributed Revenue", "ROAS", "Profit Margin", "Marketing Efficiency Ratio"]
                col.markdown(create_kpi_card(label, value, is_positive=is_positive), unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

with main_col2:
    # Check if the unified DataFrame is ready for plotting
    if not merged_df.empty:
        fig_line = go.Figure()
        
        # Plotting directly from merged_df is much cleaner
        fig_line.add_trace(go.Scatter(x=merged_df['date'], y=merged_df['spend'], name='Marketing Spend', line=dict(color='#FFA726')))
        fig_line.add_trace(go.Scatter(x=merged_df['date'], y=merged_df['attributed revenue'], name='Attributed Revenue', line=dict(color='#4A90E2')))
        fig_line.add_trace(go.Scatter(x=merged_df['date'], y=merged_df['total revenue'], name='Total Business Revenue', line=dict(color='#388E3C')))

        with st.container(border=True):
            st.markdown('<div class="chart-title">Performance Trends</div>', unsafe_allow_html=True)
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
            go.Bar(name="Spend", x=summary["platform"], y=summary["spend"], marker_color='#4A90E2'),
            go.Bar(name="Revenue", x=summary["platform"], y=summary["attributed revenue"], marker_color='#388E3C')
        ])
        
        with st.container(border=True):
            st.markdown('<div class="chart-title">Platform Performance</div>', unsafe_allow_html=True)
            fig_platform = style_figure(fig_platform)
            fig_platform.update_layout(barmode="group")
            st.plotly_chart(fig_platform, use_container_width=True, config={'displayModeBar': False})

with chart_col2:
    # --- Top Campaigns Table (This part is the same) ---
    if not combined_platforms.empty and 'campaign' in combined_platforms.columns:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Top Campaigns by Revenue</div>', unsafe_allow_html=True)

            campaigns_df = combined_platforms.groupby("campaign")[["spend", "attributed revenue"]].sum()
            campaigns_df['ROAS'] = campaigns_df['attributed revenue'] / campaigns_df['spend']
            campaigns_df = campaigns_df.sort_values("attributed revenue", ascending=False).head(6).reset_index()

            def format_currency(val):
                if val >= 1_000_000:
                    return f"${val/1_000_000:.1f}M"
                if val >= 1_000:
                    return f"${val/1_000:.0f}k"
                return f"${val:,.0f}"

            campaigns_df['spend'] = campaigns_df['spend'].apply(format_currency)
            campaigns_df['attributed revenue'] = campaigns_df['attributed revenue'].apply(format_currency)
            campaigns_df['ROAS'] = campaigns_df['ROAS'].apply(lambda x: f"{x:.2f}x")
            
            campaigns_df.set_index('campaign', inplace=True)
            st.table(campaigns_df)

    # --- NEW: KPI cards to fill the empty space below the table ---
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True) # Adds vertical space

    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    
    with kpi_col1:
        st.markdown(create_kpi_card("Avg. Order Value", f"${aov:,.2f}"), unsafe_allow_html=True)
    
    with kpi_col2:
        st.markdown(create_kpi_card("Cost Per Click", f"${cpc:,.2f}"), unsafe_allow_html=True)

    with kpi_col3:
        st.markdown(create_kpi_card("Profit on Ad Spend", f"{poas:.2f}x"), unsafe_allow_html=True)
# ----------------------
if not business_filtered.empty:
    insight_col1, insight_col2 = st.columns([1, 1])
    
    with insight_col1:
        if not merged_df.empty:
            fig_revenue = go.Figure(data=[
                go.Scatter(
                    x=merged_df['date'], y=merged_df['total revenue'], fill='tonexty',
                    mode='lines', name='Total Revenue', line=dict(color='#4A90E2')
                ),
                go.Scatter(
                    x=merged_df['date'], y=merged_df['gross profit'], fill='tozeroy',
                    mode='lines', name='Gross Profit', line=dict(color='#388E3C')
                )
            ])
            with st.container(border=True):
                st.markdown('<div class="chart-title"> Revenue vs Profit</div>', unsafe_allow_html=True)
                fig_revenue = style_figure(fig_revenue)
                st.plotly_chart(fig_revenue, use_container_width=True, config={'displayModeBar': False})
    
    with insight_col2:
        if not merged_df.empty:
            fig_customers = go.Figure()
            
            fig_customers.add_trace(go.Bar(
            x=merged_df['date'], y=merged_df['new customers'],
            name='New Customers',
            marker_color='#388E3C',
            opacity=0.8
            ))
            
            # Bar for New Orders
            fig_customers.add_trace(go.Bar(
                x=merged_df['date'], y=merged_df['# of new orders'],
                name='New Orders',
                marker_color='#4A90E2',
                opacity=0.8
            ))
            
            with st.container(border=True):
                st.markdown('<div class="chart-title">Customer Trends</div>', unsafe_allow_html=True)
                fig_customers = style_figure(fig_customers)
                fig_customers.update_layout(
                    yaxis2=dict(title="", overlaying='y', side='right'),
                    yaxis=dict(title=""),
                    legend=dict(x=0, y=1.0) # Adjust legend to not overlap title
                )
                st.plotly_chart(fig_customers, use_container_width=True, config={'displayModeBar': False})