import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import yfinance as yf           # <--- Ini yang hilang
import pandas as pd

# 1. Load Konfigurasi
load_dotenv()

# 2. Susun DB_URL (Gunakan f-string agar rapi)
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT')

# Tambahkan ?sslmode=require karena Neon mewajibkan SSL
DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

# 3. Inisialisasi engine (Sekarang DB_URL sudah terdefinisi)
engine = create_engine(DB_URL)

def update_assets(tickers):
    """Memastikan daftar ticker terdaftar di tabel assets"""
    print("Mengecek daftar aset di database...")
    with engine.connect() as conn:
        for ticker, name, category in tickers:
            query = text("""
                INSERT INTO assets (ticker, asset_name, category)
                VALUES (:t, :n, :c)
                ON CONFLICT (ticker) DO NOTHING
            """)
            conn.execute(query, {"t": ticker, "n": name, "c": category})
            conn.commit()

def fetch_and_load_price(ticker):
    """Ambil data harga dan masukkan ke database dengan handling MultiIndex"""
    print(f"Mengambil data untuk {ticker}...")
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT asset_id FROM assets WHERE ticker = :t"), {"t": ticker})
        row_asset = result.fetchone()
        if not row_asset:
            print(f"Error: Ticker {ticker} belum terdaftar di tabel assets.")
            return
        asset_id = row_asset[0]

    # Ambil data dari yfinance
    data = yf.download(ticker, period="7d", interval="1d", auto_adjust=False)
    
    if data.empty:
        print(f"Peringatan: Tidak ada data untuk {ticker}")
        return

    # Meratakan MultiIndex jika ada
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    data = data.reset_index()

    with engine.connect() as conn:
        for _, row in data.iterrows():
            adj_close = row.get('Adj Close', row.get('Close'))
            
            query = text("""
                INSERT INTO daily_prices (asset_id, price_date, open_price, close_price, adj_close, volume)
                VALUES (:aid, :d, :o, :c, :ac, :v)
                ON CONFLICT (asset_id, price_date) DO NOTHING
            """)
            conn.execute(query, {
                "aid": asset_id,
                "d": row['Date'],
                "o": row['Open'],
                "c": row['Close'],
                "ac": adj_close,
                "v": int(row['Volume']) if pd.notnull(row['Volume']) else 0
            })
        conn.commit()
    print(f"Data {ticker} berhasil diupdate!")

if __name__ == "__main__":
    # Daftar aset yang ingin dipantau
    watchlist = [
        ("BBCA.JK", "Bank Central Asia", "Stock"),
        ("AAPL", "Apple Inc.", "Stock"),
        ("BTC-USD", "Bitcoin", "Crypto")
    ]
    
    # Jalankan proses ETL
    update_assets(watchlist)
    for ticker, _, _ in watchlist:
        fetch_and_load_price(ticker)