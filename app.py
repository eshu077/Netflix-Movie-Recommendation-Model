import pickle
import pandas as pd
import streamlit as st
import requests
import time

# Load movie data and similarity matrix
data = pickle.load(open('movie_dict.pkl', 'rb'))
data = pd.DataFrame(data)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# Function to fetch poster with retry logic
def fetch_poster(movie_id, retries=3):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=1afed7e5cf27e4c0068fa3f9f8906cba'
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
        except Exception:
            time.sleep(0.5)
    return "https://via.placeholder.com/500x750?text=No+Image"

# Recommendation logic with poster validation
def recommend(movie):
    movie_index = data[data['title'] == movie].index[0]
    distance = similarity[movie_index]
    movie_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        if len(recommended_movies) >= 5:
            break

        movie_data = data.iloc[i[0]]
        movie_title = movie_data.title
        movie_id = movie_data.get('movie_id', None)

        if pd.notna(movie_id):
            poster = fetch_poster(int(movie_id))
        else:
            poster = "https://via.placeholder.com/500x750?text=No+Image"

        recommended_movies.append(movie_title)
        recommended_posters.append(poster)

    return recommended_movies, recommended_posters

# Streamlit UI with enhanced styling
st.set_page_config(page_title="🎬 Movie Recommendation System", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main-title {
        font-size: 40px;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 30px;
    }
    .movie-card {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.2s ease-in-out;
    }
    .movie-card:hover {
        transform: scale(1.03);
        background-color: #ffe6e6;
    }
    img {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-title">🎬 Movie Recommendation System</div>', unsafe_allow_html=True)

# Movie selection
selected_movie = st.selectbox('📽️ Choose a movie to get similar recommendations:', data['title'].values)
btn = st.button('✨ Recommend')

# Recommendation display
if btn:
    with st.spinner('🔍 Finding your cinematic matches...'):
        names, posters = recommend(selected_movie)
        cols = st.columns(len(names))
        for i in range(len(names)):
            with cols[i]:
                st.markdown(f"""
                    <div class="movie-card">
                        <h4>{names[i]}</h4>
                        <img src="{posters[i]}" width="150">
                    </div>
                """, unsafe_allow_html=True)
