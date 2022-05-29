import ml_algo
from flask import Flask, render_template, request, url_for, redirect
import requests
import random
import os

# Enter Api key
TMDB_API_KEY = os.getenv('tmdb_api_key', default='c9230db9478a7ec04437999aad76658e')
TMBD_MOVIE_DETAILS_PATH = "https://api.themoviedb.org/3/movie/"

PARAMS = {
    'api_key': TMDB_API_KEY
}

# Get the list of top 10 recommended movies using the simple recommender
top = ml_algo.top_picks()
random.shuffle(top)
top = top[0:10]

# Creating for the autoComplete feature
suggestions = ml_algo.get_suggestions()


def chart_builder(genre: str):
    """
    Builds, shuffles and returns top 10 movies in a genre.

    Parameters
    ----------
    genre: Type of movies.

    Returns
    -------
    A list of 10 tuples. Each tuple consists of movie details.
    """
    chart = ml_algo.build_chart(genre)
    random.shuffle(chart)
    return chart[:10]


def recommender(query, **kwargs):
    """
    Takes a movie present in the dataset or keywords to return the most similar movie using content-based filtering.
    Parameters
    ----------
    query: Keywords or Movie Names.
    kwargs: Used if the searched query is a movie in the dataset.

    Returns
    -------
    List of ids of all the similar movies to the specified query.
    """
    similar_movies = []
    if kwargs:
        similar_movies.append(kwargs['first'])
    similar_movies_id = ml_algo.improved_recommendations(query)
    for i in similar_movies_id:
        request = requests.get(TMBD_MOVIE_DETAILS_PATH + str(i), params=PARAMS).json()
        similar_movies.append((request['title'], request['poster_path'], i))
    return similar_movies


# Building charts
action = chart_builder('Action')
adventure = chart_builder('Adventure')
romance = chart_builder('Romance')
comedy = chart_builder('Comedy')


def create_list(genre):
    """
    Creates a list of all the top movies in a genre.
    Parameters
    ----------
    genre: Type of moive.

    Returns
    -------
    List of tuples.
    """
    temp_list = []
    for i in genre:
        request = requests.get(TMBD_MOVIE_DETAILS_PATH + str(i), params=PARAMS).json()
        temp_list.append((request['title'], request['poster_path'], i))
    return temp_list


top_list = create_list(top)
action_list = create_list(action)
adventure_list = create_list(adventure)
romance_list = create_list(romance)
comedy_list = create_list(comedy)

movies = {'Picks': top_list,
          'Action': action_list,
          'Adventure': adventure_list,
          'Romance': romance_list,
          'Comedy': comedy_list
          }

app = Flask(__name__, template_folder='templates')


# Home page
@app.route("/")
def index():
    return render_template('index.html', suggestions=suggestions, movies=movies)


# Movie view page. Gives information about the movie and shows a preview of the movie. Also shows movies similar to it.
@app.route("/movie/<int:id>")
def movie_details(id):
    # id is the tmdb movie id
    movie = {}

    # Used the tmdb api to get movie detailsl
    details = requests.get(TMBD_MOVIE_DETAILS_PATH + str(id), params=PARAMS).json()
    vid_request = requests.get(TMBD_MOVIE_DETAILS_PATH + str(id) + '/videos', params=PARAMS).json()
    crew = requests.get(TMBD_MOVIE_DETAILS_PATH + str(id) + '/credits', params=PARAMS).json()
    movie['title'] = details['title']
    movie['overview'] = details['overview']
    movie['video_key'] = vid_request['results'][0]['key']
    movie['actor'] = []
    movie['crew'] = []
    for i in range(3):
        movie['actor'].append(crew['cast'][i]['name'])
    for i in range(3):
        movie['crew'].append(crew['crew'][i]['name'])
    movie['similar_movies'] = recommender(movie['title'])
    return render_template('movie_info.html', suggestions=suggestions, movie=movie)


# A route which accepts the submitted query in the search box and passes it on to display results.
@app.route("/search", methods=["POST"])
def search():
    q = request.form.get('query')
    return redirect(url_for('search_results', query=q))


# Displays all the similar movies to the query.
@app.route("/search/<string:query>")
def search_results(query):
    idx = ml_algo.present(query)
    first = ''
    if idx != '':
        request = requests.get(TMBD_MOVIE_DETAILS_PATH + str(idx), params=PARAMS).json()
        first = (request['title'], request['poster_path'], idx)
    if first:
        movie_list = recommender(query, first=first)
    else:
        movie_list = recommender(query)
    return render_template('search_results.html', suggestions=suggestions, movies_search=movie_list)


if __name__ == '__main__':
    app.run(debug=True)
