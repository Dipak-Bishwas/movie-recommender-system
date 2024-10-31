from flask import Flask, render_template, request
import pickle
import requests
import pandas as pd

app = Flask(__name__)

# Function to fetch movie poster from TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    else:
        return None

# Function to recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names = []
    recommended_movie_posters = []
    
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]]['movie_id']  # Correct way to access the movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]]['title'])
    
    return recommended_movie_names, recommended_movie_posters

# Load movie list and similarity matrix
movies = pickle.load(open('model/movie_dict.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

# Check if movies is a dictionary and convert to DataFrame if needed
if isinstance(movies, dict):
    movies = pd.DataFrame(movies)  # Convert the dictionary to a DataFrame

# Flask Routes
@app.route('/')
def index():
    movie_list = movies['title'].tolist()  # Use .tolist() to get a list of titles
    return render_template('index.html', movie_list=movie_list)

@app.route('/recommend', methods=['POST'])
def recommend_movies():
    movie = request.form['movie']
    recommended_movie_names, recommended_movie_posters = recommend(movie)
    return render_template('index.html', movie_list=movies['title'].tolist(), 
                           recommendations=zip(recommended_movie_names, recommended_movie_posters))

if __name__ == '__main__':
    app.run(debug=True)
