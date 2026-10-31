import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Mengatur konfigurasi halaman agar lebar dan rapi
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Mengatur style seaborn
sns.set(style='darkgrid')

# Fungsi untuk memuat dan membersihkan data


@st.cache_data
def load_data():
    # Pastikan file 'day.csv' berada dalam satu folder yang sama dengan dashboard.py
    df = pd.read_csv('main_data.csv')

    # Data Wrangling & Cleaning sederhana
    df['dteday'] = pd.to_datetime(df['dteday'])
    df['season'] = df['season'].map(
        {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'})
    df['weathersit'] = df['weathersit'].map(
        {1: 'Clear/Few Clouds', 2: 'Mist/Cloudy', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Ice'})
    df['workingday'] = df['workingday'].map(
        {0: 'Holiday/Weekend', 1: 'Working Day'})

    return df


df_day = load_data()

# --- SIDEBAR (FILTER INTERAKTIF) ---
st.sidebar.header("🔍 Filter Data")

# Filter berdasarkan Musim (Season)
season_options = df_day['season'].unique().tolist()
selected_seasons = st.sidebar.multiselect(
    "Pilih Musim:",
    options=season_options,
    default=season_options
)

# Filter dataframe berdasarkan pilihan sidebar
filtered_df = df_day[df_day['season'].isin(selected_seasons)]

# --- HALAMAN UTAMA DASHBOARD ---
st.title("🚲 Dashboard Analisis Penyewaan Sepeda (Bike Sharing)")
st.markdown("Dashboard interaktif ini dirancang untuk menyajikan hasil analisis data penyewaan sepeda secara visual dan dinamis guna memenuhi kriteria submission Dicoding.")

# Menampilkan Ringkasan Metrik Utama (KPIs)
col1, col2, col3 = st.columns(3)
with col1:
    total_rentals = filtered_df['cnt'].sum()
    st.metric("Total Penyewaan", value=f"{total_rentals:,}")
with col2:
    avg_rentals = int(filtered_df['cnt'].mean()
                      ) if not filtered_df.empty else 0
    st.metric("Rata-rata Harian", value=f"{avg_rentals:,}")
with col3:
    total_days = filtered_df.shape[0]
    st.metric("Total Hari Tercatat", value=total_days)

st.markdown("---")

# Layout Grafik menjadi 2 kolom atau berurutan ke bawah
st.subheader("Visualisasi Hasil Analisis Bisnis")

# Grafik 1: Pertanyaan 1 (Working Day vs Holiday/Weekend)
st.markdown(
    "#### 1. Perbandingan Rata-rata Penyewaan: Hari Kerja vs Hari Libur/Weekend")
fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(
    x='workingday',
    y='cnt',
    data=filtered_df,
    palette='Set2',
    estimator='mean',
    errorbar=None,
    ax=ax
)
ax.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Kategori Hari',
             fontsize=11, fontweight='bold')
ax.set_xlabel('Kategori Hari', fontsize=10)
ax.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=10)
st.pyplot(fig)

# Grafik 2: Pertanyaan 2 (Weather Situation)
st.markdown("#### 2. Pengaruh Kondisi Cuaca terhadap Rata-rata Penyewaan Sepeda")
fig2, ax2 = plt.subplots(figsize=(10, 4))
sns.barplot(
    x='weathersit',
    y='cnt',
    data=filtered_df,
    palette='Blues_d',
    estimator='mean',
    errorbar=None,
    ax=ax2
)
ax2.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca',
              fontsize=11, fontweight='bold')
ax2.set_xlabel('Kondisi Cuaca', fontsize=10)
ax2.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=10)
plt.xticks(rotation=15)
st.pyplot(fig2)

# Footer
st.markdown("---")
st.caption(
    "Dibuat untuk penugasan Proyek Analisis Data Dicoding | Oleh Luthfi Nur Adli")