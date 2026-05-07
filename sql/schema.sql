CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) UNIQUE NOT NULL,
    asset_name VARCHAR(100),
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE daily_prices (
    price_id SERIAL PRIMARY KEY,
    asset_id INT REFERENCES assets(asset_id),
    price_date DATE NOT NULL,
    open_price DECIMAL(18, 4),
    close_price DECIMAL(18, 4),
    adj_close DECIMAL(18, 4),
    volume BIGINT,
    UNIQUE(asset_id, price_date) -- Mencegah duplikasi data di tanggal yang sama
);

CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    asset_id INT REFERENCES assets(asset_id),
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(10) CHECK (transaction_type IN ('BUY', 'SELL')),
    quantity DECIMAL(18, 8) NOT NULL,
    price_per_unit DECIMAL(18, 4) NOT NULL,
    fees DECIMAL(18, 4) DEFAULT 0
);