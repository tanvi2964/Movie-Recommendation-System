# ========================================
# MOVIE RECOMMENDER SYSTEM (Streamlit App)
# ========================================

import streamlit as st
import pickle
import pandas as pd
import requests
import os
import time
from pathlib import Path

# ================================
# 🔑 TMDB API Configuration
# ================================
# 👉 Replace this with your own TMDB API key
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

# ================================
# 🎞 Fetch Movie Poster from TMDB
# ================================
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    """
    Fetches movie poster from TMDB API with timeout handling and fallback image.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=25)  # Increased timeout
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
    except requests.exceptions.Timeout:
        st.warning("⏳ TMDB API timed out. Showing placeholder instead.")
        return "https://via.placeholder.com/500x750?text=Timeout"
    except Exception as e:
        st.warning(f"⚠️ Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=Error"

# ================================
# 🎬 Recommendation Function
# ================================
def recommend(movie):
    """
    Returns a list of recommended movies and their posters.
    """
    if movie not in movies['title'].values:
        st.error("❌ Movie not found in the database.")
        return [], []

    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:  # Top 5 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        time.sleep(1)  # Prevent API throttling
        recommended_movie_posters.append(fetch_poster(movie_id))

    return recommended_movie_names, recommended_movie_posters

# ================================
# 📂 Load Model Files Safely
# ================================
model_path = Path("model")
if not model_path.exists():
    model_path.mkdir(parents=True, exist_ok=True)

try:
    movies = pickle.load(open(model_path / "movie_list.pkl", "rb"))
    similarity = pickle.load(open(model_path / "similarity.pkl", "rb"))
except FileNotFoundError:
    st.error("❌ Model files not found! Make sure 'movie_list.pkl' and 'similarity.pkl' are in the 'model/' folder.")
    st.stop()

# ================================
# 🖥 Streamlit UI
# ================================
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.title("🍿 Movie Recommender System")

st.write("Select a movie from the list below to get similar recommendations:")

selected_movie = st.selectbox(
    "🎥 Choose a movie:",
    movies['title'].values
)

if st.button("Show Recommendations"):
    with st.spinner("🔍 Fetching similar movies..."):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    if recommended_movie_names:
        st.subheader("🎯 Recommended Movies for You:")
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.image(recommended_movie_posters[idx], use_container_width=True)
                st.caption(recommended_movie_names[idx])
    else:
        st.info("No recommendations found. Try another movie.")
