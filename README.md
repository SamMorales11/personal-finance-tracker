<img width="1527" height="881" alt="Screenshot 2026-05-11 112300" src="https://github.com/user-attachments/assets/429411d9-1f1b-4c2d-b5b2-a7e755e86e34" />

## 🚀 Automated Personal Finance & Investment Tracker

**Automated Personal Finance & Investment Tracker** adalah sistem analisis data investasi *end-to-end* yang dirancang untuk mengotomatisasi seluruh siklus hidup data mulai dari ekstraksi data pasar secara *real-time*, pemrosesan berbasis cloud, hingga visualisasi interaktif.

Sistem ini menghilangkan kebutuhan intervensi manual dalam pemantauan portofolio dengan memanfaatkan *orchestration* berbasis waktu untuk memastikan data selalu mutakhir bagi pengguna.

---

## 🏗️ System Architecture

Proyek ini dibangun dengan prinsip modularitas untuk memisahkan antara pengambilan data (Ingestion), penyimpanan (Storage), dan penyajian (Presentation).



1.  **Extraction:** Script Python menggunakan library `yfinance` untuk mengambil data historis dan harian dari instrumen pasar modal dan aset kripto.
2.  **Orchestration:** **GitHub Actions** bertindak sebagai mandor otomatis yang menjalankan script ETL setiap hari pada pukul 00:00 UTC (07:00 WIB).
3.  **Storage:** Data disimpan dalam database **PostgreSQL** di cloud (**Neon Tech**) dengan skema yang dioptimalkan untuk performa data deret waktu (*time-series*).
4.  **Transformation:** Logika analisis seperti *Moving Averages* dan *Trend Signals* diproses langsung di tingkat database menggunakan **SQL Views** untuk efisiensi komputasi.
5.  **Visualization:** Dashboard interaktif dibangun menggunakan **Streamlit** dan **Plotly** untuk memberikan *insight* visual yang elegan dan mudah dipahami.

---

## ✨ Key Features

* **Daily Automated ETL:** Pembaruan data otomatis tanpa perlu intervensi manual setiap hari.
* **Technical Analytics:** Perhitungan otomatis untuk indikator teknikal seperti Moving Average (MA5 & MA20) dan Daily Returns.
* **Market Signals:** Penentuan sinyal pasar *Bullish* dan *Bearish* secara otomatis berdasarkan analisis data historis.
* **Interactive Charts:** Visualisasi pergerakan harga yang bersih dan responsif dengan fitur *hover* data.
* **Cloud Native Architecture:** Seluruh infrastruktur berjalan di cloud, memungkinkan sistem tetap bekerja secara independen dari perangkat lokal.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Language** | Python 3.11+ |
| **Database** | PostgreSQL (Neon Tech) |
| **Library Data** | Pandas, SQLAlchemy, yfinance |
| **Orchestration** | GitHub Actions |
| **Visualization** | Streamlit, Plotly |
| **Security** | Dotenv (Environment Variables) |

---

## 🚀 Getting Started

### 1. Prasyarat
* Python 3.11 atau versi lebih tinggi terinstal.
* Akun [Neon.tech](https://neon.tech) untuk akses database PostgreSQL cloud.

### 2. Instalasi
Clone repositori ini dan instal seluruh dependensi yang diperlukan:
```bash
git clone [https://github.com/SamMorales11/personal-finance-tracker.git](https://github.com/SamMorales11/personal-finance-tracker.git)
cd personal-finance-tracker
pip install -r requirements.txt
