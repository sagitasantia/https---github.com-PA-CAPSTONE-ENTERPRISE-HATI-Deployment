import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from streamlit_option_menu import option_menu
import base64
# from sklearn.cluster import AgglomerativeClustering

# Function to read image file as base64
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(img):
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

st.set_page_config(page_title="Tania Syar'i", layout="wide")

img = get_img_as_base64("bg baju.jpg")
set_background(img)

logo = "logo_5_web-removebg-preview.png"

@st.cache_data
def load_data():
    data = pd.read_csv('Data Modeling.csv', index_col=0)
    return data

def load_data_asli():
    data = pd.read_csv('Data Asli.csv', index_col=0)
    return data

data = load_data()
data_asli = load_data_asli()

st.title("Dashboard Analisis Data Produk UMKM Tania Syar'i")

with st.sidebar:
    st.image(logo, use_column_width=True)
    st.markdown("<h1 style='font-size: 30px; font-weight: bold; font-family: Arial, sans-serif;'>Selamat datang</h1>", unsafe_allow_html=True)
    selected = option_menu("Pilih Menu", ['EDA','Clustering'],
                           icons=['bar-chart-fill', 'bricks'],
                           menu_icon="cast", default_index=0)

if selected == 'EDA':
    pilar = st.selectbox("Pilih Pilar", ['Distribusi', 'Perbandingan', 'Komposisi', 'Hubungan'])
    
    if pilar == 'Distribusi':
        st.subheader("Distribusi Data Berdasarkan Nama")

        # Menghitung 10 nama dengan laba terbesar
        top_names = data.groupby('Nama')['Laba'].sum().nlargest(10).index

        # Memfilter data untuk hanya mencakup 10 nama 
        filtered_data = data[data['Nama'].isin(top_names)]

        pilih_column = st.selectbox("Pilih Kolom ", ['Modal', 'Laba'])

        # Menggunakan grafik batang
        fig = px.bar(filtered_data, x='Nama', y=pilih_column, color='Nama', title=f"Hubungan Nama dengan {pilih_column} untuk 10 Nama dengan Laba Tertinggi")

        st.plotly_chart(fig, use_container_width=True)
        if pilih_column == 'Modal':
            st.write("Grafik batang ini menampilkan perubahan nilai modal dari 10 nama dengan laba tertinggi. Grafik ini memudahkan kita untuk membandingkan nilai modal antara berbagai nama secara langsung dan melihat tren kenaikan atau penurunan.")
        elif pilih_column == 'Laba':
            st.write("Grafik batang ini menampilkan laba dari 10 nama dengan laba tertinggi. Setiap batang mewakili satu nama, dan tinggi batang mencerminkan laba. Variasi tinggi batang menunjukkan fluktuasi laba, memungkinkan analisis visual tentang nama mana yang paling menguntungkan atau mengalami penurunan")
            
    elif pilar == 'Perbandingan':
        st.subheader("Perbandingan Rata-Rata Modal dan Laba Per Nama")

        # Menghitung rata-rata modal dan laba per nama
        data_grouped = data.groupby('Nama').agg({'Modal': 'mean', 'Laba': 'mean'}).reset_index()

        # Mengurutkan data berdasarkan 'Nama'
        data_grouped = data_grouped.sort_values(by=['Modal', 'Laba'], ascending=False)
        # Membuat grafik batang untuk rata-rata modal dan laba per nama
        fig = px.bar(data_grouped, x=['Modal', 'Laba'], y='Nama', title="Rata-Rata Modal dan Laba Per Nama")
        st.plotly_chart(fig, use_container_width=True)
        st.write("Grafik batang ini menampilkan rata-rata modal dan laba untuk setiap nama. Ini memberikan gambaran tentang kinerja keuangan setiap nama.")

    elif pilar == 'Komposisi':
        st.subheader("Komposisi Data")

        top_n = st.number_input('Show top N categories', min_value=1, value=10, step=1)
        nama_count = data['Nama'].value_counts().nlargest(top_n).reset_index()
        nama_count.columns = ['Nama', 'Count']

        # Mengurutkan data berdasarkan 'Count'
        nama_count = nama_count.sort_values(by='Count', ascending=False)

        chart = alt.Chart(nama_count).mark_bar().encode(
            x=alt.X('Count:Q', title='Frekuensi'), 
            y=alt.Y('Nama:N', title='Nama', sort='-x'),  
            tooltip=[alt.Tooltip('Nama:N', title='Nama'), alt.Tooltip('Count:Q', title='Frekuensi')]
        ).properties(
            title="Count Plot dari 'Nama'"
        ).interactive()

        st.altair_chart(chart, use_container_width=True)
        st.write("Grafik ini adalah count plot yang menampilkan frekuensi dari berbagai nama model pakaian. Pada sumbu horizontal, kita melihat 'Frekuensi' dan pada sumbu vertikal tercantum 'Nama' model pakaian tersebut. Grafik ini membantu memvisualisasikan model pakaian mana yang paling sering muncul dalam data yang diberikan. Model dengan frekuensi tertinggi muncul di bagian atas grafik.")

    elif pilar == 'Hubungan':
        st.subheader("Hubungan Antar Variabel")
        
        selected_columns = ['Laba', 'Modal', 'Jual']
        
        correlation_matrix = data[selected_columns].corr()

        fig = px.imshow(correlation_matrix,
                        labels=dict(x="Variable", y="Variable", color="Correlation"),x=selected_columns,y=selected_columns,text_auto=True, color_continuous_scale='viridis')  
        
        fig.update_layout(title="Heatmap Korelasi Antar Variabel", xaxis_nticks=36, yaxis_nticks=36)

        st.plotly_chart(fig, use_container_width=True)
        st.write("Heatmap ini menunjukkan bahwa laba sangat berkorelasi dengan jumlah penjualan, tapi kurang berkorelasi dengan modal. Semakin banyak penjualan, semakin tinggi laba yang cenderung didapat. Modal tidak secara konsisten berpengaruh terhadap laba atau penjualan, menunjukkan bahwa peningkatan modal tidak selalu menghasilkan laba atau penjualan yang lebih tinggi.")

elif selected == 'Clustering':
    st.subheader("Analisis Kluster")
    clustering_columns = [col for col in data.columns if col not in ['cluster_hc', 'cluster_kmeans','category_laba','Nama']]
    selected_columns = st.multiselect("Pilih Kolom untuk Klustering", clustering_columns, default=["Jual", "Laba"])
    n_clusters = 4
    if len(selected_columns) >= 2:
        X = data[selected_columns]
        data['Cluster'] = data['cluster_hc'] 
        cluster_distribution = data.groupby('Cluster')['Nama'].value_counts().reset_index(name='Count')
        cluster_summary = data.groupby('Cluster').agg({'Jual': ['mean', 'median'], 'Laba': ['mean', 'median']}).reset_index()
        st.subheader("Detail Segmentasi Per Kluster")
        cluster_details = {cluster: data[data['Cluster'] == cluster] for cluster in range(n_clusters)}
        for cluster in cluster_details:
            if cluster_details[cluster][['Nama', 'Jual', 'Laba']].duplicated().any():
                st.write(f"Detail Kluster {cluster}: ")
                st.dataframe(cluster_details[cluster][['Nama', 'Jual', 'Laba']].drop_duplicates().sort_values('Jual', ascending=False))

        st.subheader("Korelasi Fitur Kluster")
        correlation_matrix = data[selected_columns + ['Cluster']].corr().reset_index()
        correlation_data = correlation_matrix.melt('index')
        heatmap = alt.Chart(correlation_data).mark_rect().encode(x='index:N',y='variable:N',color='value:Q',tooltip=[ alt.Tooltip('index:N', title='Feature 1'),alt.Tooltip('variable:N', title='Feature 2'), alt.Tooltip('value:Q', title='Correlation')]
        ).properties(
            title="Heatmap of Feature Correlation"
        ).interactive()

        st.altair_chart(heatmap, use_container_width=True)
        st.write("Heatmap menunjukkan korelasi antara variabel dalam analisis kluster. Kluster tidak langsung berdasarkan penjualan atau laba, menunjukkan korelasi negatif dengan keduanya. Namun, penjualan dan laba memiliki korelasi positif, menunjukkan bahwa peningkatan penjualan biasanya berhubungan dengan peningkatan laba. Ini menandakan bahwa kluster mungkin dibentuk berdasarkan faktor lain yang tidak termasuk dalam heatmap ini.")
        st.subheader("Kluster")
        for cluster in range(n_clusters):
            st.markdown(f"**Kluster {cluster}:**")
            st.markdown(f"Rata-rata Harga Jual: {cluster_summary.loc[cluster_summary['Cluster'] == cluster, ('Jual', 'mean')].values[0]}")
            st.markdown(f"Rata-rata Laba: {cluster_summary.loc[cluster_summary['Cluster'] == cluster, ('Laba', 'mean')].values[0]}")
            st.markdown("---")

        st.subheader("Filter Data Berdasarkan Kluster")
        selected_cluster = st.selectbox("Pilih Kluster untuk Difilter", range(n_clusters))
        filtered_data = data[data['Cluster'] == selected_cluster]
        st.dataframe(filtered_data)


        st.subheader("Visualisasi Distribusi Model Baju per Kluster")
        bars = alt.Chart(cluster_distribution).mark_bar().encode( x='Count:Q', y=alt.Y('Nama:N', sort='-x'), color='Cluster:N').properties(
            width=alt.Step(40), 
            title="Distribusi Model Baju per Kluster"
        )
        text = bars.mark_text( align='left', baseline='middle', dx=3).encode( text='Count:Q')
        chart = (bars + text).interactive()
        st.altair_chart(chart, use_container_width=True)
        if selected_cluster == 0:
             st.write("Produk di kluster 0, dengan harga jual rata-rata 437,576 dan laba rata-rata 90,303, adalah barang premium berkualitas tinggi atau eksklusif. Oleh karena itu, kluster 0 dipilih untuk segmentasi dan rekomendasi produk, karena menunjukkan kinerja keuangan kuat dan menarik bagi konsumen yang bersedia membayar lebih. Fokus pada produk ini dapat memaksimalkan keuntungan dan membantu dalam strategi pemasaran dan inventaris.")
       
       
    else:
        st.error("Pilih minimal dua kolom untuk klustering.")

st.markdown("---")
st.caption("UMKM Tania Syar'i - Analisis Data Produk")
