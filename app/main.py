import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# ==========================================
# 1. KONFIGURASI HALAMAN & STYLE
# ==========================================
st.set_page_config(page_title="Investment Tracker Pro", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 700 !important; }
    .main .block-container { padding-top: 2rem; padding-left: 3rem; padding-right: 3rem; }
    section[data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #374151; }
    .main-header { font-size: 2.2rem; font-weight: 700; letter-spacing: -0.05rem; margin-bottom: 0.5rem; }
    .sub-header { color: #9CA3AF; margin-bottom: 2rem; font-size: 1rem; }
    hr { margin: 2rem 0 !important; border: 0; border-top: 1px solid #374151; }
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
    # Mengambil data dari view yang sudah kita buat
    query = "SELECT * FROM v_asset_performance ORDER BY price_date DESC"
    return pd.read_sql(query, engine)

try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.stop()

# ==========================================
# 3. SIDEBAR & HEADER
# ==========================================
with st.sidebar:
    st.markdown("### Navigation")
    menu = st.radio("Go to:", ["Main Dashboard", "Advanced Insights"])
    
    st.markdown("---")
    st.markdown("### System Status")
    st.success("GitHub Actions: Active")
    st.info("Database: Neon PostgreSQL")

st.markdown('<div class="main-header">Investment Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated Portfolio Management Dashboard</div>', unsafe_allow_html=True)

# ==========================================
# 4. HALAMAN UTAMA (DASHBOARD)
# ==========================================
if menu == "Main Dashboard":
    asset_list = sorted(df['ticker'].unique())
    latest_all = df.groupby('ticker').first().reset_index()
    
    cols = st.columns(len(asset_list))
    for i, ticker in enumerate(asset_list):
        row = latest_all[latest_all['ticker'] == ticker].iloc[0]
        with cols[i]:
            st.metric(label=f"{ticker}", value=f"${row['adj_close']:,.2f}", delta=f"{row['daily_return_pct']:.2f}%")

    st.markdown("<hr>", unsafe_allow_html=True)
    
    col_chart, col_data = st.columns([2, 1], gap="large")
    with col_chart:
        selected_ticker = st.selectbox("Pilih Aset untuk Analisis Harga", asset_list)
        chart_data = df[df['ticker'] == selected_ticker].sort_values('price_date')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=chart_data['price_date'], y=chart_data['adj_close'], mode='lines', name='Price', line=dict(color='#3B82F6', width=2)))
        fig.add_trace(go.Scatter(x=chart_data['price_date'], y=chart_data['ma_5'], mode='lines', name='MA 5', line=dict(color='#10B981', width=1, dash='solid')))
        fig.add_trace(go.Scatter(x=chart_data['price_date'], y=chart_data['ma_20'], mode='lines', name='MA 20', line=dict(color='#F59E0B', width=1, dash='dot')))
        
        fig.update_layout(hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=450, legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)

    with col_data:
        st.subheader("Historical Activity")
        display_df = chart_data[['price_date', 'adj_close', 'daily_return_pct', 'trend_signal']].tail(10)
        st.dataframe(display_df.sort_values('price_date', ascending=False), use_container_width=True, hide_index=True)

# ==========================================
# 5. HALAMAN ADVANCED INSIGHTS
# ==========================================
elif menu == "Advanced Insights":
    st.subheader("Deep Portfolio Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Correlation", "Allocation", "Drawdown Risk"])
    
    with tab1:
        st.markdown("#### Asset Correlation Matrix")
        # Pivot data untuk menghitung korelasi
        corr_df = df.pivot(index='price_date', columns='ticker', values='adj_close').pct_change().corr()
        fig_corr = px.imshow(corr_df, text_auto=".2f", color_continuous_scale='RdBu_r', aspect="auto")
        fig_corr.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_corr, use_container_width=True)
        st.info("💡 Nilai mendekati 1.00 berarti aset bergerak searah. Nilai mendekati 0 atau negatif berarti diversifikasi yang baik.")

    with tab2:
        st.markdown("#### Asset Allocation (By Category)")
        # Menghitung jumlah aset per kategori (Karena kita belum punya data kuantitas transaksi)
        alloc_data = df.groupby('ticker').first().groupby('category').size().reset_index(name='count')
        fig_pie = px.pie(alloc_data, values='count', names='category', hole=.4, color_discrete_sequence=['#3B82F6', '#10B981'])
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab3:
        st.markdown("#### Historical Drawdown Analysis")
        selected_dd = st.selectbox("Pilih Aset untuk Analisis Resiko", df['ticker'].unique())
        dd_data = df[df['ticker'] == selected_dd].sort_values('price_date')
        
        # Hitung Drawdown: (Price / Rolling Max) - 1
        rolling_max = dd_data['adj_close'].cummax()
        drawdown = (dd_data['adj_close'] / rolling_max) - 1
        
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(x=dd_data['price_date'], y=drawdown * 100, fill='tozeroy', name='Drawdown', line=dict(color='#EF4444', width=1)))
        fig_dd.update_layout(yaxis_title="Drawdown (%)", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig_dd, use_container_width=True)
        
        max_dd = drawdown.min() * 100
        st.error(f"📉 **Maximum Drawdown Historis:** {max_dd:.2f}%")