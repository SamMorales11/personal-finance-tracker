**🚀 Automated Personal Finance & Investment Tracker**
Automated Personal Finance & Investment Tracker adalah sistem analisis data investasi end-to-end yang dirancang untuk mengotomatisasi seluruh siklus hidup data—mulai dari ekstraksi data pasar secara real-time, pemrosesan berbasis cloud, hingga visualisasi interaktif.

Sistem ini menghilangkan kebutuhan intervensi manual dalam pemantauan portofolio dengan memanfaatkan orchestration berbasis waktu untuk memastikan data selalu mutakhir.

**🏗️ System Architecture**
Proyek ini dibangun dengan prinsip modularitas untuk memisahkan antara pengambilan data (Ingestion), penyimpanan (Storage), dan penyajian (Presentation).

Extraction: Script Python menggunakan library yfinance untuk mengambil data historis dan harian dari pasar saham dan kripto.

Orchestration: GitHub Actions bertindak sebagai mandor otomatis yang menjalankan script ETL setiap hari pada pukul 00:00 UTC.

Storage: Data disimpan dalam database PostgreSQL di cloud (Neon Tech) dengan skema yang dioptimalkan untuk data deret waktu (time-series).

Transformation: Logika analisis seperti Moving Averages dan Trend Signals diproses langsung di tingkat database menggunakan SQL Views.

Visualization: Dashboard interaktif dibangun dengan Streamlit dan Plotly untuk memberikan insight visual yang cepat dan elegan.
