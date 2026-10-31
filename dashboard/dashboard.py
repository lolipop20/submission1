import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

sns.set(style="darkgrid")

# ----------------------------------------------------------------------------
# Load & prepare data
# ----------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))


@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(current_dir, "main_data.csv"))
    df["dteday"] = pd.to_datetime(df["dteday"])

    season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    weather_map = {
        1: "Clear/Few Clouds",
        2: "Mist/Cloudy",
        3: "Light Snow/Rain",
        4: "Heavy Rain/Ice",
    }
    workingday_map = {0: "Non Working Day", 1: "Working Day"}
    month_names = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                   7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

    # Jaga kolom asli berkode angka untuk sorting/filtering, tambahkan kolom label
    if df["season"].dtype != object:
        df["season_label"] = df["season"].map(season_map)
    else:
        df["season_label"] = df["season"]

    if df["weathersit"].dtype != object:
        df["weathersit_label"] = df["weathersit"].map(weather_map)
    else:
        df["weathersit_label"] = df["weathersit"]

    if df["workingday"].dtype != object:
        df["workingday_label"] = df["workingday"].map(workingday_map)
    else:
        df["workingday_label"] = df["workingday"]

    df["month_name"] = df["mnth"].map(month_names)
    df["year"] = df["dteday"].dt.year

    return df


day_df = load_data()

# ----------------------------------------------------------------------------
# Sidebar - filter dinamis
# ----------------------------------------------------------------------------
st.sidebar.header("Filter Data")

min_date = day_df["dteday"].min().date()
max_date = day_df["dteday"].max().date()

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

year_options = sorted(day_df["year"].unique().tolist())
selected_years = st.sidebar.multiselect(
    "Tahun", options=year_options, default=year_options
)

season_options = ["Spring", "Summer", "Fall", "Winter"]
selected_seasons = st.sidebar.multiselect(
    "Musim", options=season_options, default=season_options
)

# Terapkan filter ke dataframe utama -> semua visualisasi di bawah
# akan ikut berubah secara dinamis sesuai pilihan filter ini.
filtered_df = day_df[
    (day_df["dteday"].dt.date >= start_date)
    & (day_df["dteday"].dt.date <= end_date)
    & (day_df["year"].isin(selected_years))
    & (day_df["season_label"].isin(selected_seasons))
]

st.sidebar.markdown(f"**Jumlah hari terpilih:** {len(filtered_df)} hari")

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.title("🚲 Dashboard Analisis Bike Sharing")
st.markdown(
    "Dashboard ini menjawab dua pertanyaan bisnis utama: perbandingan penyewaan "
    "pada hari kerja vs hari libur beserta tren bulanannya, serta pengaruh "
    "kondisi cuaca terhadap tingkat penyewaan sepeda."
)

if filtered_df.empty:
    st.warning(
        "Tidak ada data pada rentang filter yang dipilih. Silakan ubah filter di sidebar.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Total Penyewaan", f"{filtered_df['cnt'].sum():,.0f}")
col2.metric("Rata-rata Penyewaan/Hari", f"{filtered_df['cnt'].mean():,.0f}")
col3.metric("Jumlah Hari Terpilih", f"{len(filtered_df):,}")

st.divider()

# ----------------------------------------------------------------------------
# Pertanyaan 1: Working Day vs Non Working Day + tren bulanan
# ----------------------------------------------------------------------------
st.header("Pertanyaan 1: Working Day vs Non Working Day & Puncak Bulanan")

st.subheader("Total Penyewaan: Working Day vs Non Working Day")
wd_stats = filtered_df.groupby("workingday_label")["cnt"].sum().reset_index()

fig1, ax1 = plt.subplots(figsize=(8, 5))
bars = sns.barplot(
    data=wd_stats, x="workingday_label", y="cnt",
    hue="workingday_label", palette="Set2", legend=False, ax=ax1
)
for container in ax1.containers:
    ax1.bar_label(container, fmt="%.0f", padding=3)
ax1.set_title("Total Penyewaan per Kategori Hari",
              fontsize=11, fontweight="bold")
ax1.set_xlabel("Kategori Hari")
ax1.set_ylabel("Total Penyewaan (cnt)")
st.pyplot(fig1)

if len(wd_stats) == 2:
    working_total = wd_stats.loc[wd_stats["workingday_label"]
                                 == "Working Day", "cnt"].values
    nonworking_total = wd_stats.loc[wd_stats["workingday_label"]
                                    == "Non Working Day", "cnt"].values
    if len(working_total) and len(nonworking_total) and nonworking_total[0] > 0:
        diff_pct = (working_total[0] - nonworking_total[0]
                    ) / nonworking_total[0] * 100
        st.caption(
            f"Total penyewaan pada Working Day {diff_pct:+.1f}% dibanding "
            f"Non Working Day pada rentang data terpilih."
        )

st.subheader("Tren Total Penyewaan per Bulan")
month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
monthly_stats = (
    filtered_df.groupby(["mnth", "month_name"])["cnt"].sum().reset_index()
    .sort_values("mnth")
)

peak_idx = monthly_stats["cnt"].idxmax()
peak_month_name = monthly_stats.loc[peak_idx, "month_name"]
peak_month_total = monthly_stats.loc[peak_idx, "cnt"]

fig2, ax2 = plt.subplots(figsize=(9, 5))
colors = ["#d62728" if m ==
          peak_month_name else "#4c72b0" for m in monthly_stats["month_name"]]
bars2 = ax2.bar(monthly_stats["month_name"],
                monthly_stats["cnt"], color=colors)
ax2.bar_label(bars2, fmt="%.0f", padding=3, rotation=90, fontsize=8)
ax2.set_title(
    f"Total Penyewaan per Bulan — Puncak: {peak_month_name} ({peak_month_total:,.0f})",
    fontsize=11, fontweight="bold"
)
ax2.set_xlabel("Bulan")
ax2.set_ylabel("Total Penyewaan (cnt)")
st.pyplot(fig2)

st.divider()

# ----------------------------------------------------------------------------
# Pertanyaan 2: Pengaruh kondisi cuaca
# ----------------------------------------------------------------------------
st.header("Pertanyaan 2: Pengaruh Kondisi Cuaca terhadap Penyewaan")

weather_stats = (
    filtered_df.groupby("weathersit_label")["cnt"].mean().reset_index()
    .sort_values("cnt", ascending=False)
)
weather_stats.rename(columns={"cnt": "mean_cnt"}, inplace=True)

if not weather_stats.empty:
    clear_row = weather_stats[weather_stats["weathersit_label"]
                              == "Clear/Few Clouds"]
    clear_mean = clear_row["mean_cnt"].values[0] if not clear_row.empty else weather_stats["mean_cnt"].max()
    weather_stats["pct_vs_clear"] = (
        (weather_stats["mean_cnt"] - clear_mean) / clear_mean * 100
    ).round(1)

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    bars3 = sns.barplot(
        data=weather_stats, x="weathersit_label", y="mean_cnt",
        order=weather_stats["weathersit_label"], hue="weathersit_label",
        palette="Blues_d", legend=False, ax=ax3
    )
    for container in ax3.containers:
        ax3.bar_label(container, fmt="%.0f", padding=3)

    for i, row in weather_stats.reset_index(drop=True).iterrows():
        if row["weathersit_label"] != "Clear/Few Clouds":
            ax3.text(
                i, row["mean_cnt"] *
                0.5, f"{row['pct_vs_clear']:+.1f}%\nvs Clear",
                ha="center", color="white", fontsize=9, fontweight="bold"
            )

    ax3.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca",
                  fontsize=12, fontweight="bold")
    ax3.set_xlabel("Kondisi Cuaca")
    ax3.set_ylabel("Rata-rata Penyewaan (cnt)")
    plt.xticks(rotation=15)
    st.pyplot(fig3)

    st.subheader("Rincian Angka per Kondisi Cuaca")
    display_table = weather_stats.rename(columns={
        "weathersit_label": "Kondisi Cuaca",
        "mean_cnt": "Rata-rata Penyewaan",
        "pct_vs_clear": "Persentase vs Clear/Few Clouds (%)",
    })
    st.dataframe(display_table.style.format({
        "Rata-rata Penyewaan": "{:.0f}",
        "Persentase vs Clear/Few Clouds (%)": "{:+.1f}",
    }), use_container_width=True)

    worst_row = weather_stats.iloc[-1]
    st.caption(
        f"Kondisi cuaca dengan penurunan terbesar: **{worst_row['weathersit_label']}** "
        f"dengan rata-rata {worst_row['mean_cnt']:,.0f} penyewaan/hari "
        f"({worst_row['pct_vs_clear']:+.1f}% dibanding Clear/Few Clouds)."
    )
else:
    st.info("Tidak ada data kondisi cuaca pada filter yang dipilih.")

st.divider()

# Footer
st.markdown("---")
st.caption(
    "Dibuat untuk penugasan Proyek Analisis Data Dicoding | Oleh Luthfi Nur Adli")