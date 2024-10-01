import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

# Membaca file CSV dan mengatur datetime
hour_df = pd.read_csv(r"C:\Users\ASUS\Submission\Dashboard\main.csv")
datetime_columns = ["dteday"]
hour_df.sort_values(by="dteday", inplace=True)
hour_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    hour_df[column] = pd.to_datetime(hour_df[column])

min_date = hour_df["dteday"].min()
max_date = hour_df["dteday"].max()

# Sidebar untuk filter rentang tanggal
with st.sidebar:
    st.image(r"C:\Users\ASUS\Submission\pngegg.png", width=200)
    start_date, end_date = st.date_input(
        label="Date Range", 
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data berdasarkan rentang tanggal yang dipilih
main_df = hour_df[(hour_df["dteday"] >= pd.to_datetime(start_date)) & 
                  (hour_df["dteday"] <= pd.to_datetime(end_date))]


#header dan deskripsi
st.title("Bike-Sharing Dashboard 🚴🏻‍♀️")
st.markdown("#### Bike Rental")

col1, col2, col3, col4 = st.columns(4) #membuat tempat/kolom untuk imformasi khusus

# Kolom untuk Total Transaksi
with col1:
    total_transaction = main_df['count_cr'].count()
    st.metric("Total Transaction", value=total_transaction)

# Kolom untuk Total Sepeda yang Disewa
with col2:
    total_rent = main_df['count_cr'].sum() 
    st.metric("Total Bikes Rented", value=total_rent)

# kolom untuk total pelanggan registered
with col3:
    total_registered = main_df['registered'].sum()
    st.metric("Total Registered", value=total_registered)

# kolom untuk total pelanggan casual
with col4:
    total_casual = main_df['casual'].sum()
    st.metric("Total Casual", value=total_casual)
    

# Fungsi untuk membuat pie chart tipe pelanggan
def customer_type(data_frame):
    st.title("Distribusi Penyewaan Sepeda berdasarkan Tipe Pelanggan")
    total_casual = data_frame["casual"].sum()
    total_registered = data_frame["registered"].sum()

    labels = ["Casual", "Registered"]
    sizes = [total_casual, total_registered]
    colors = ["#7C94A5", "#16355F"]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.2f%%")
    ax.axis("equal")

    st.pyplot(fig)

# Panggil fungsi dengan data yang sudah difilter
customer_type(main_df)

# Fungsi untuk menampilkan bar chart waktu penyewaan rendah
def plot_low_rent_hours(df):
    sum_rental_items_df = df.groupby("time_of_day").count_cr.sum().reset_index()

    fig, ax = plt.subplots(figsize=(18, 8))
    sns.barplot(x="time_of_day", y="count_cr", 
                data=sum_rental_items_df.sort_values(by="count_cr", ascending=True).head(4), 
                palette=["#16355F", "#16355F", "#16355F", "#16355F"], ax=ax)

    ax.set_ylabel("Pelanggan")
    ax.set_xlabel("Waktu", fontsize=15)
    ax.set_title("Grafik Persewaan Sepeda berdasarkan Waktu", loc="center", fontsize=30)
    ax.tick_params(axis='y', labelsize=15)
    ax.tick_params(axis='x', labelsize=15)

    plt.tight_layout()
    st.pyplot(fig)

# Panggil fungsi untuk menampilkan bar chart
plot_low_rent_hours(main_df)

# Fungsi untuk menampilkan scatter plot jumlah pelanggan maksimum per bulan
def plot_max_customers_per_month(main_df):
    fig, ax = plt.subplots(figsize=(24, 5))

    # Menghitung jumlah pelanggan maksimum per hari
    rentals_per_day = main_df['count_cr'].groupby(main_df['dteday']).max()

    # Membuat scatter plot dan line plot
    ax.scatter(rentals_per_day.index, rentals_per_day.values, c="#c88f7d", s=20, marker='o', label="Pelanggan Maks")
    ax.plot(rentals_per_day.index, rentals_per_day.values, linestyle='-', color='#16355F')

    ax.set_xlabel('Tanggal', fontsize=14)
    ax.set_ylabel('Jumlah Pelanggan', fontsize=14)
    ax.set_title('Grafik Jumlah Pelanggan Maksimum', fontsize=16)
    ax.grid(True)
    ax.legend()
    return fig

# Panggil fungsi plot
st.title("Grafik Jumlah Pelanggan Maksimum")
fig = plot_max_customers_per_month(main_df)
st.pyplot(fig)


# membuat scatter plot korelasi antara kecepatan angin dengan penyewa sepeda
def plot_scatter_windspeed_vs_renters(data_frame):
    st.title("Korelasi antara Kecepatan Angin dengan Tingkat Penyewaan Sepeda")
    plt.figure(figsize=(12,6))
    jitter = 0.01 * np.random.randn(len(data_frame))
    x_jittered = data_frame['windspeed'] + jitter

    # Scatter plot untuk penyewa casual
    plt.subplot(1, 2, 1)
    plt.scatter(data_frame['windspeed'], data_frame['casual'], color='#7C94A5', alpha=0.5)
    plt.xlabel('Kecepatan Angin')
    plt.ylabel('Jumlah Penyewa Casual')
    plt.title('Hubungan antara Kecepatan Angin dan Penyewa Casual')

    # Scatter plot untuk penyewa registered
    plt.subplot(1, 2, 2)
    plt.scatter(data_frame['windspeed'], data_frame['registered'], color='#7C94A5', alpha=0.5)
    plt.xlabel('Kecepatan Angin')
    plt.ylabel('Jumlah Penyewa Registered')
    plt.title('Hubungan antara Kecepatan Angin dan Penyewa Registered')

    plt.tight_layout()
    st.pyplot(plt)

# Panggil fungsi dengan data yang sudah difilter berdasarkan rentang tanggal
plot_scatter_windspeed_vs_renters(main_df)


def analyze_rfm_registered_users(hour_df):
    rfm_df = hour_df.groupby(by="registered", as_index=False).agg({
        "instant": "count",  # Frequency
        "count_cr": "max",      # Monetary
        "dteday": lambda x: (pd.Timestamp.now() - x.max()).days  # Recency
    })
    rfm_df.columns = ["registered", "frequency", "monetary", "recency"]
    
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))

    bar_colors = ["#16355F"] * 5

    sns.barplot(y="recency", x="registered", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=bar_colors, ax=axes[0])
    axes[0].set_title("Recency (days)", fontsize=18)

    sns.barplot(y="frequency", x="registered", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=bar_colors, ax=axes[1])
    axes[1].set_title("Frequency", fontsize=18)

    sns.barplot(y="monetary", x="registered", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=bar_colors, ax=axes[2])
    axes[2].set_title("Monetary", fontsize=18)

    plt.suptitle("Pelanggan Terdaftar (Registered) Terbaik dengan Analisis RFM", fontsize=20)
    st.pyplot(fig)

# Fungsi untuk Analisis RFM pengguna casual
def analyze_rfm_casual_users(hour_df):
    rfm_data = hour_df.groupby(by="casual", as_index=False).agg({
        "instant": "count",  # Frequency
        "count_cr": "max",      # Monetary
        "dteday": lambda x: (pd.Timestamp.now() - x.max()).days  # Recency
    })
    rfm_data.columns = ["casual", "frequency", "monetary", "recency"]
    
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))

    bar_colors = ["#16355F"] * 5

    sns.barplot(y="recency", x="casual", data=rfm_data.sort_values(by="recency", ascending=True).head(5), palette=bar_colors, ax=axes[0])
    axes[0].set_title("Recency (days)", fontsize=18)

    sns.barplot(y="frequency", x="casual", data=rfm_data.sort_values(by="frequency", ascending=False).head(5), palette=bar_colors, ax=axes[1])
    axes[1].set_title("Frequency", fontsize=18)

    sns.barplot(y="monetary", x="casual", data=rfm_data.sort_values(by="monetary", ascending=False).head(5), palette=bar_colors, ax=axes[2])
    axes[2].set_title("Monetary", fontsize=18)

    plt.suptitle("Pelanggan Kasual Terbaik dengan Analisis RFM", fontsize=20)
    st.pyplot(fig)

# Pemanggilan Fungsi di Streamlit
st.title("Analisis RFM Pengguna Sepeda")


# Menggunakan fitur button, untuk memilih apakah ingin mengecek registered aatau casual users
if st.button("Analisis RFM Registered Users"): 
    analyze_rfm_registered_users(hour_df)

if st.button("Analisis RFM Casual Users"):
    analyze_rfm_casual_users(hour_df)