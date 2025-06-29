import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Dashboard Analisis Penggunaan Media Sosial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kustomisasi CSS untuk tampilan
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #00d4ff;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #444;
        text-align: center;
    }
    .notes-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-top: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_and_clean_data():
    """
    Membuat DataFrame sampel yang lebih kaya untuk analisis mendalam.
    Fungsi ini sekarang mencakup Jenis Kelamin, Tingkat Pendidikan, Durasi Tidur,
    Skor Kesehatan Mental, dan Platform yang digunakan.
    """
    try:
        n_samples = 300
        # Membuat data dasar
        data = {
            'Jenis Kelamin': np.random.choice(['Laki-laki', 'Perempuan'], n_samples, p=[0.48, 0.52]),
            'Tingkat Pendidikan': np.random.choice(
                ['Pelajar SMA', 'Mahasiswa S1', 'Mahasiswa Pascasarjana'],
                n_samples, p=[0.4, 0.5, 0.1]
            ),
            'Durasi_Penggunaan_Harian': np.random.uniform(1, 12, n_samples).round(1),
            'Platform_Terbanyak_Digunakan': np.random.choice(
                ['Instagram', 'TikTok', 'X (Twitter)', 'YouTube', 'Facebook'],
                n_samples, p=[0.3, 0.35, 0.15, 0.15, 0.05]
            )
        }
        df = pd.DataFrame(data)

        # Membuat korelasi yang lebih realistis antar variabel
        # Semakin lama penggunaan medsos, semakin rendah durasi tidur & skor kesehatan
        base_sleep = np.random.normal(7.5, 1, n_samples)
        df['Durasi_Tidur'] = (base_sleep - df['Durasi_Penggunaan_Harian'] * 0.2).clip(3, 10).round(1)

        base_mental_health = np.random.normal(75, 10, n_samples)
        df['Skor_Kesehatan_Mental'] = (base_mental_health - df['Durasi_Penggunaan_Harian'] * 2.5).clip(10, 100).astype(int)

        return df

    except Exception as e:
        st.error(f"Error saat membuat data simulasi: {str(e)}")
        return None

# ===== FUNGSI VISUALISASI BARU =====

def visualisasi_demografi(df):
    """
    Insight 1: Perbandingan penggunaan medsos berdasarkan demografi.
    """
    st.subheader("1. Penggunaan Media Sosial Berdasarkan Demografi")

    # Agregasi data
    agg_df = df.groupby(['Tingkat Pendidikan', 'Jenis Kelamin'])['Durasi_Penggunaan_Harian'].mean().round(2).reset_index()

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(
            agg_df,
            x='Tingkat Pendidikan',
            y='Durasi_Penggunaan_Harian',
            color='Jenis Kelamin',
            barmode='group',
            title='Rata-rata Jam Penggunaan Medsos Harian',
            labels={
                'Durasi_Penggunaan_Harian': 'Rata-rata Jam Penggunaan',
                'Tingkat Pendidikan': 'Tingkat Pendidikan',
                'Jenis Kelamin': 'Jenis Kelamin'
            },
            text_auto=True,
            color_discrete_map={'Laki-laki': '#1E90FF', 'Perempuan': '#FF69B4'}
        )
        fig.update_layout(
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis_title="Rata-rata Jam per Hari",
            xaxis_title=None
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="notes-box">', unsafe_allow_html=True)
        st.markdown("<h5>💡 Insight & Analisis</h5>", unsafe_allow_html=True)
        st.markdown("""
        Visualisasi ini membandingkan rata-rata durasi penggunaan media sosial harian antara laki-laki dan perempuan di berbagai tingkat pendidikan.
        
        **Tujuan:**
        - Mengidentifikasi apakah gender atau tingkat pendidikan mempengaruhi durasi penggunaan medsos.
        - Menemukan kelompok demografis mana yang paling banyak menghabiskan waktu di media sosial.
        
        **Analisis Data:**
        """)
        # Menampilkan data agregat
        st.dataframe(agg_df.style.highlight_max(axis=0, subset=['Durasi_Penggunaan_Harian'], color='#FF6B6B'))
        st.markdown('</div>', unsafe_allow_html=True)


def visualisasi_korelasi(df):
    """
    Insight 2: Korelasi antara penggunaan medsos, durasi tidur, dan kesehatan mental.
    """
    st.subheader("2. Korelasi Penggunaan Medsos, Durasi Tidur, dan Kesehatan Mental")

    rel_cols = ['Durasi_Penggunaan_Harian', 'Durasi_Tidur', 'Skor_Kesehatan_Mental']
    corr_matrix = df[rel_cols].corr()

    col1, col2 = st.columns([2, 1])
    with col1:
        # Heatmap Korelasi
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r', # Red-Blue reversed
            zmin=-1, zmax=1,
            title="Heatmap Korelasi Antar Variabel Kunci"
        )
        fig.update_layout(
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="notes-box">', unsafe_allow_html=True)
        st.markdown("<h5>💡 Insight & Analisis</h5>", unsafe_allow_html=True)
        st.markdown("""
        Heatmap ini menunjukkan kekuatan dan arah hubungan antar variabel. Semakin gelap warnanya, semakin kuat korelasinya.
        
        **Insight dan Analisis:**
        """)
        
        # Mengambil nilai korelasi secara dinamis dari dataframe
        corr_health = corr_matrix.loc['Durasi_Penggunaan_Harian', 'Skor_Kesehatan_Mental']
        corr_sleep = corr_matrix.loc['Durasi_Penggunaan_Harian', 'Durasi_Tidur']
        corr_sleep_health = corr_matrix.loc['Durasi_Tidur', 'Skor_Kesehatan_Mental']
        
        # Menampilkan interpretasi sesuai nilai pada gambar Anda
        st.markdown(f"""
        * **Korelasi Negatif Sangat Kuat ({corr_health:.2f}):** Terdapat hubungan negatif yang sangat signifikan antara **Durasi Penggunaan Medsos** dan **Skor Kesehatan Mental**. Ini adalah temuan paling kuat, yang berarti semakin lama seseorang menggunakan media sosial, skor kesehatan mentalnya cenderung semakin rendah.
        
        * **Korelasi Negatif Sedang ({corr_sleep:.2f}):** Ditemukan hubungan negatif sedang antara **Durasi Penggunaan Medsos** dan **Durasi Tidur**. Ini menunjukkan bahwa peningkatan waktu di media sosial berkaitan dengan berkurangnya jam tidur.
        
        * **Korelasi Positif Sedang ({corr_sleep_health:.2f}):** Menariknya, terdapat hubungan positif sedang antara **Durasi Tidur** dan **Skor Kesehatan Mental**, yang menyiratkan bahwa tidur yang cukup berpotensi meningkatkan kesehatan mental.
        """)
        st.markdown('</div>', unsafe_allow_html=True)



def visualisasi_platform(df):
    """
    Insight 3: Mengidentifikasi platform yang paling 'adiktif'.
    """
    st.subheader("3. Platform Media Sosial Paling Banyak Menyita Waktu")
    
    # Agregasi data
    platform_df = df.groupby('Platform_Terbanyak_Digunakan')['Durasi_Penggunaan_Harian'].agg(['mean', 'count']).round(1).reset_index()
    platform_df.rename(columns={'mean': 'Rata_Rata_Durasi', 'count': 'Jumlah_Pengguna'}, inplace=True)
    platform_df = platform_df.sort_values('Rata_Rata_Durasi', ascending=False)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(
            platform_df,
            x='Rata_Rata_Durasi',
            y='Platform_Terbanyak_Digunakan',
            orientation='h',
            title='Rata-rata Jam Penggunaan Harian per Platform',
            labels={
                'Rata_Rata_Durasi': 'Rata-rata Jam Penggunaan per Hari',
                'Platform_Terbanyak_Digunakan': 'Platform Media Sosial'
            },
            text='Rata_Rata_Durasi'
        )
        fig.update_layout(
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="notes-box">', unsafe_allow_html=True)
        st.markdown("<h5>💡 Insight & Analisis</h5>", unsafe_allow_html=True)
        st.markdown("""
        Grafik ini mengurutkan platform media sosial berdasarkan rata-rata waktu harian yang dihabiskan oleh penggunanya.
        
        **Tujuan:**
        - Mengidentifikasi platform mana yang paling 'adiktif' atau menyita waktu.
        - Memberikan dasar untuk menentukan prioritas intervensi atau kampanye edukasi.""")
        st.dataframe(platform_df)
        st.markdown('</div>', unsafe_allow_html=True)

# ===== FUNGSI UTAMA (MAIN) =====

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Dashboard Analisis Penggunaan Media Sosial</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_and_clean_data()
    if df is None: return

    # Sidebar Filters
    st.sidebar.title("⚙️ Filter Data")
    
    # Filter Tingkat Pendidikan
    pendidikan_options = ['Semua'] + list(df['Tingkat Pendidikan'].unique())
    selected_pendidikan = st.sidebar.selectbox("Pilih Tingkat Pendidikan", pendidikan_options)
    
    # Filter Jenis Kelamin
    gender_options = ['Semua'] + list(df['Jenis Kelamin'].unique())
    selected_gender = st.sidebar.selectbox("Pilih Jenis Kelamin", gender_options)

    # Terapkan filter
    filtered_df = df.copy()
    if selected_pendidikan != 'Semua':
        filtered_df = filtered_df[filtered_df['Tingkat Pendidikan'] == selected_pendidikan]
    if selected_gender != 'Semua':
        filtered_df = filtered_df[filtered_df['Jenis Kelamin'] == selected_gender]

    st.sidebar.markdown("---")
    st.sidebar.info(f"Menampilkan **{len(filtered_df)}** dari **{len(df)}** total responden.")


    # Metrik Utama
    st.subheader("📈 Metrik Utama Berdasarkan Filter")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown('<div class="metric-card"><h5>Total Responden</h5><h3>{}</h3></div>'.format(len(filtered_df)), unsafe_allow_html=True)
    with m_col2:
        avg_usage = filtered_df['Durasi_Penggunaan_Harian'].mean()
        st.markdown('<div class="metric-card"><h5>Avg. Durasi Medsos</h5><h3>{:.1f} Jam/Hari</h3></div>'.format(avg_usage), unsafe_allow_html=True)
    with m_col3:
        avg_sleep = filtered_df['Durasi_Tidur'].mean()
        st.markdown('<div class="metric-card"><h5>Avg. Durasi Tidur</h5><h3>{:.1f} Jam/Malam</h3></div>'.format(avg_sleep), unsafe_allow_html=True)
    with m_col4:
        avg_health = filtered_df['Skor_Kesehatan_Mental'].mean()
        st.markdown('<div class="metric-card"><h5>Avg. Skor Kesehatan</h5><h3>{:.0f} / 100</h3></div>'.format(avg_health), unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Menampilkan visualisasi
    visualisasi_demografi(filtered_df)
    st.markdown("<hr>", unsafe_allow_html=True)
    visualisasi_korelasi(filtered_df)
    st.markdown("<hr>", unsafe_allow_html=True)
    visualisasi_platform(filtered_df)
    
    # Footer
    st.markdown("---")
    st.markdown("**🚀 Dashboard Analisis Penggunaan Media Sosial - ADHIM KHAIRIL ANAM**")

if __name__ == "__main__":
    main()