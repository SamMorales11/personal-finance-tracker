import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# ==========================================
# 1. KONFIGURASI HALAMAN & STYLE
# ==========================================
st.set_page_config(
    page_title="Personal Finance Tracker", 
    layout="wide", 
    page_icon="📊"
)

# Custom CSS untuk tampilan profesional dan minimalis
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem !important;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #374151;
    }

    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.05rem;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #9CA3AF;
        margin-bottom: 2rem;
        font-size: 1rem;
    }
    
    hr {
        margin: 2rem 0 !important;
        border: 0;
        border-top: 1px solid #374151;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA DATA
# ==========================================
load_dotenv()

@st.cache_resource
def get_engine():
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?sslmode=require"
    return create_engine(db_url)

engine = get_engine()

@st.cache_data(ttl=3600)
def load_data():
    query = "SELECT * FROM v_asset_performance ORDER BY price_date DESC"
    return pd.read_sql(query, engine)

try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal memuat data. Error: {e}")
    st.stop()

# ==========================================
# 3. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### 🔍 Filter Portfolio")
    asset_list = sorted(df['ticker'].unique())
    selected_ticker = st.selectbox("Pilih Aset untuk Detail", asset_list)
    
    st.markdown("---")
    st.markdown("### ℹ️ System Status")
    st.success("GitHub Actions: Active")
    st.info("Database: Neon PostgreSQL")

# ==========================================
# 4. HEADER UTAMA
# ==========================================
st.markdown('<div class="main-header">Personal Finance Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated End-to-End Analytics Pipeline via GitHub Actions</div>', unsafe_allow_html=True)

# ==========================================
# 5. KPI METRICS (ROW 1)
# ==========================================
latest_all = df.groupby('ticker').first().reset_index()
cols = st.columns(len(asset_list))

for i, ticker in enumerate(asset_list):
    row = latest_all[latest_all['ticker'] == ticker].iloc[0]
    with cols[i]:
        st.metric(
            label=f"{ticker}",
            value=f"${row['adj_close']:,.2f}",
            delta=f"{row['daily_return_pct']:.2f}%"
        )

st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# 6. VISUALISASI UTAMA (ROW 2)
# ==========================================
col_chart, col_data = st.columns([2, 1], gap="large")

with col_chart:
    st.subheader(f"Price Analysis: {selected_ticker}")
    chart_data = df[df['ticker'] == selected_ticker].sort_values('price_date')
    
    fig = go.Figure()

    # Harga Utama - Garis lebih tipis (width=2) dan tanpa fill untuk kejelasan
    fig.add_trace(go.Scatter(
        x=chart_data['price_date'], y=chart_data['adj_close'],
        mode='lines', name='Price',
        line=dict(color='#3B82F6', width=2),
    ))

    # Moving Average 5 - Ultra thin (width=1)
    fig.add_trace(go.Scatter(
        x=chart_data['price_date'], y=chart_data['ma_5'],
        mode='lines', name='MA 5 (Short)',
        line=dict(color='#10B981', width=1, dash='solid')
    ))

    # Moving Average 20 - Ultra thin dotted (width=1)
    fig.add_trace(go.Scatter(
        x=chart_data['price_date'], y=chart_data['ma_20'],
        mode='lines', name='MA 20 (Med)',
        line=dict(color='#F59E0B', width=1, dash='dot')
    ))

    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(
            orientation="h", 
            yanchor="bottom", y=1.05, 
            xanchor="right", x=1,
            font=dict(size=10, color="#9CA3AF")
        ),
        xaxis=dict(
            showgrid=False, 
            linecolor='#374151',
            tickfont=dict(size=10, color="#9CA3AF")
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='#1F2937', 
            zeroline=False,
            tickfont=dict(size=10, color="#9CA3AF")
        ),
        height=450
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col_data:
    st.subheader("Historical Activity")
    display_df = chart_data[['price_date', 'adj_close', 'daily_return_pct', 'trend_signal']].tail(10)
    display_df.columns = ['Date', 'Price', 'Return %', 'Signal']
    
    st.dataframe(
        display_df.sort_values('Date', ascending=False),
        use_container_width=True,
        column_config={
            "Date": st.column_config.DateColumn(format="MMM DD, YYYY"),
            "Return %": st.column_config.NumberColumn(format="%.2f%%"),
            "Price": st.column_config.NumberColumn(format="$%.2f"),
        },
        hide_index=True
    )

    latest_signal = display_df.iloc[-1]['Signal']
    signal_color = "#10B981" if latest_signal == "Bullish" else "#EF4444"
    st.markdown(f"""
        <div style="background-color: #1F2937; padding: 15px; border-radius: 8px; border-left: 4px solid {signal_color};">
            <small style="color: #9CA3AF; font-weight: 600; text-transform: uppercase; font-size: 0.7rem;">Current Market Signal</small><br>
            <strong style="font-size: 1.1rem; color: {signal_color};">{latest_signal} Trend</strong>
        </div>
    """, unsafe_allow_html=True)