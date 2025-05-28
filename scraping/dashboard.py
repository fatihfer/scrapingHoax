import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from pymongo import MongoClient
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string
import re

# Unduh resource NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Koneksi ke MongoDB
client = MongoClient("mongodb+srv://fatihfernando01:123@cluster0.4kz97zw.mongodb.net/")
db = client["berita"]
collection = db["hoax_teridentifikasi"]

# Ambil data dari MongoDB dan ubah jadi DataFrame
data = pd.DataFrame(list(collection.find()))
if '_id' in data.columns:
    data = data.drop(columns=['_id'])

# Bersihkan data kosong
data.dropna(subset=['title', 'body'], inplace=True)

# Judul Dashboard
st.title("📊 Dashboard Deteksi Berita Hoax")

# ------------------------------
# 1. Daftar Judul Berita
# ------------------------------
st.header("📰 Daftar Judul Berita")
st.write(data[['title', 'url']])

# ------------------------------
# 2. WordCloud dari Isi Berita
# ------------------------------
st.header("☁️ WordCloud dari Isi Berita")

# Proses cleansing
text = " ".join(data['body'].astype(str)).lower()
text = re.sub(r'\d+', '', text)  # Hapus angka
text = text.translate(str.maketrans('', '', string.punctuation))  # Hapus tanda baca
tokens = word_tokenize(text)

# Stopwords
stop_words_wc = set(stopwords.words('indonesian'))
stop_words_wc.update(['halaman', 'klik', 'baca', 'juga', 'yang', 'untuk', 'pada', 'dengan', 'selengkapnya', 'sumber', 'akun','narasi','foto', 'referensi', 'facebook', 'salah','berita', 'beredar', 'kategori', 'video', 'klarifikasi'])

tokens_wc = [word for word in tokens if word not in stop_words_wc and len(word) > 2]
cleaned_text = " ".join(tokens_wc)

# WordCloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(cleaned_text)
st.image(wordcloud.to_array(), use_container_width=True)

# ------------------------------
# 2b. WordCloud dari Judul Berita
# ------------------------------
st.header("📝 WordCloud dari Judul Berita")

# Proses cleansing judul
title_text = " ".join(data['title'].astype(str)).lower()
title_text = re.sub(r'\d+', '', title_text)
title_text = title_text.translate(str.maketrans('', '', string.punctuation))
title_tokens = word_tokenize(title_text)

# Stopwords untuk judul
stop_words_title = set(stopwords.words('indonesian'))
stop_words_title.update(['halaman', 'klik', 'baca', 'juga', 'yang', 'untuk', 'pada', 'dengan', 'selengkapnya', 'sumber', 'akun','narasi','foto', 'referensi', 'salah','berita', 'beredar', 'kategori', 'klarifikasi'])

title_tokens_clean = [word for word in title_tokens if word not in stop_words_title and len(word) > 2]
title_cleaned_text = " ".join(title_tokens_clean)

# Generate dan tampilkan WordCloud untuk judul
wordcloud_title = WordCloud(width=800, height=400, background_color='white').generate(title_cleaned_text)
st.image(wordcloud_title.to_array(), use_container_width=True)

# ------------------------------
# 3. Grafik Panjang Artikel
# ------------------------------
st.header("📏 Panjang Artikel (Jumlah Kata per Berita)")
data['length'] = data['body'].apply(lambda x: len(str(x).split()))
st.bar_chart(data[['title', 'length']].set_index('title'))

# ------------------------------
# 4. Jumlah Berita per Bulan
# ------------------------------
st.header("📆 Jumlah Berita per Bulan")

data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
data['month'] = data['timestamp'].dt.to_period('M')
monthly_count = data['month'].value_counts().sort_index()

fig, ax = plt.subplots()
monthly_count.plot(kind='bar', ax=ax)
ax.set_ylabel("Jumlah Berita")
ax.set_xlabel("Bulan")
ax.set_title("Jumlah Berita per Bulan")
st.pyplot(fig)

# ------------------------------
# 5. 15 Kata yang Paling Sering Muncul
# ------------------------------
st.header("🔠 15 Kata yang Paling Sering Muncul")

stop_words_freq = set(stopwords.words('indonesian'))
stop_words_freq.update(['halaman', 'klik', 'baca', 'juga', 'yang', 'untuk', 'pada', 'dengan', 'selengkapnya', 'sumber', 'akun','narasi','foto', 'referensi', 'facebook', 'salah','berita', 'beredar', 'kategori', 'video', 'klarifikasi'])

tokens_freq = [word for word in tokens if word not in stop_words_freq and len(word) > 2]
word_freq = Counter(tokens_freq)
most_common = word_freq.most_common(15)

words, counts = zip(*most_common)
fig2, ax2 = plt.subplots()
ax2.bar(words, counts)
ax2.set_ylabel("Frekuensi")
ax2.set_title("15 Kata Paling Sering Muncul")
plt.xticks(rotation=45)
st.pyplot(fig2)
