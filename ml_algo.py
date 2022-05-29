import pandas as pd
import numpy as np
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.snowball import SnowballStemmer

import warnings

warnings.simplefilter('ignore')

md = pd.read_csv('./Dataset/movies_metadata.csv')

md['genres'] = md['genres'].fillna('[]').apply(literal_eval).apply(
    lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

md['year'] = pd.to_datetime(md['release_date'], errors='coerce').apply(
    lambda x: str(x).split('-')[0] if x != np.nan else np.nan)

links_small = pd.read_csv('./Dataset/links_small.csv')
links_small = links_small[links_small['tmdbId'].notnull()]['tmdbId'].astype('int')
credits_file = pd.read_csv('./Dataset/credits.csv')
keywords = pd.read_csv('./Dataset/keywords.csv')
keywords['id'] = keywords['id'].astype('int')
credits_file['id'] = credits_file['id'].astype('int')

md = md.drop([19730, 29503, 35587])

md['id'] = md['id'].astype('int')

md = md.merge(credits_file, on='id')
md = md.merge(keywords, on='id')
md.drop_duplicates(subset="imdb_id",
                   keep='first', inplace=True)

md = md[md['id'].isin(links_small)]
md = md.reset_index()

vote_counts = md[md['vote_count'].notnull()]['vote_count'].astype('int')
vote_averages = md[md['vote_average'].notnull()]['vote_average'].astype('int')
C = vote_averages.mean()

m = vote_counts.quantile(0.95)

qualified = md[(md['vote_count'] >= m) & (md['vote_count'].notnull()) & (md['vote_average'].notnull())][
    ['title', 'year', 'vote_count', 'vote_average', 'popularity', 'genres', 'id']]
qualified['vote_count'] = qualified['vote_count'].astype('int')
qualified['vote_average'] = qualified['vote_average'].astype('int')


def weighted_rating(x):
    v = x['vote_count']
    R = x['vote_average']
    return (v / (v + m) * R) + (m / (m + v) * C)


qualified['wr'] = qualified.apply(weighted_rating, axis=1)

qualified = qualified.sort_values('wr', ascending=False).head(20)

top_pick = list(qualified['id'])

s = md.apply(lambda x: pd.Series(x['genres']), axis=1).stack().reset_index(level=1, drop=True)
s.name = 'genre'
gen_md = md.drop('genres', axis=1).join(s)

md['cast'] = md['cast'].apply(literal_eval)
md['crew'] = md['crew'].apply(literal_eval)
md['keywords'] = md['keywords'].apply(literal_eval)
md['cast_size'] = md['cast'].apply(lambda x: len(x))
md['crew_size'] = md['crew'].apply(lambda x: len(x))


def get_director(x):
    for i in x:
        if i['job'] == 'Director':
            return i['name']
    return np.nan


md['director'] = md['crew'].apply(get_director)

md['cast'] = md['cast'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
md['cast'] = md['cast'].apply(lambda x: x[:3] if len(x) >= 3 else x)

md['keywords'] = md['keywords'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

md['cast'] = md['cast'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])

md['director'] = md['director'].astype('str').apply(lambda x: str.lower(x.replace(" ", "")))
md['director'] = md['director'].apply(lambda x: [x, x, x])

s = md.apply(lambda x: pd.Series(x['keywords']), axis=1).stack().reset_index(level=1, drop=True)
s.name = 'keyword'

s = s.value_counts()

s = s[s > 1]

stemmer = SnowballStemmer('english')


def filter_keywords(x):
    words = []
    for i in x:
        if i in s:
            words.append(i)
    return words


md['keywords'] = md['keywords'].apply(filter_keywords)

md['keywords'] = md['keywords'].apply(lambda x: [stemmer.stem(i) for i in x])

md['keywords'] = md['keywords'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])

md['soup'] = md['keywords'] + md['cast'] + md['director'] + md['genres']
md['soup'] = md['soup'].apply(lambda x: ' '.join(x))

md['soup'] = md['soup'] + " " + md['overview'].str.lower().fillna('')

count = CountVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
count_matrix = count.fit_transform(md['soup'])

cosine_sim = cosine_similarity(count_matrix, count_matrix)

md = md.reset_index()
titles = md['title']
indices = pd.Series(md.index, index=md['title'])


def build_chart(genre, percentile=0.85):
    df = gen_md[gen_md['genre'] == genre]
    vote_counts = df[df['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = df[df['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(percentile)

    qualified = df[(df['vote_count'] >= m) & (df['vote_count'].notnull()) & (df['vote_average'].notnull())][
        ['title', 'year', 'vote_count', 'vote_average', 'popularity', 'id']]
    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')

    qualified['wr'] = qualified.apply(
        lambda x: (x['vote_count'] / (x['vote_count'] + m) * x['vote_average']) + (m / (m + x['vote_count']) * C),
        axis=1)
    qualified = qualified.sort_values('wr', ascending=False).head(20)
    return list(qualified['id'])


def improved_recommendations(title):
    passed_title = " ".join(title.lstrip().rstrip().split()).title()
    if passed_title in indices:
        idx = indices[passed_title]
        if isinstance(idx, pd.Series):
            idx = idx[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
    else:
        data = {9082: stemmer.stem(passed_title.lower())}
        ser = pd.Series(data)
        temp_mat = md['soup'].append(ser)
        count_matrix_2 = count.fit_transform(temp_mat)
        cosine_sim_2 = cosine_similarity(count_matrix_2, count_matrix_2)
        sim_scores = list(enumerate(cosine_sim_2[-1]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:31]
    movie_indices = [i[0] for i in sim_scores]
    movies = md.iloc[movie_indices][['title', 'vote_count', 'vote_average', 'year', 'id']]
    vote_counts = movies[movies['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = movies[movies['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(0.50)
    qualified = movies[
        (movies['vote_count'] >= m) & (movies['vote_count'].notnull()) & (movies['vote_average'].notnull())]
    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')
    qualified['wr'] = qualified.apply(
        lambda x: (x['vote_count'] / (x['vote_count'] + m) * x['vote_average']) + (m / (m + x['vote_count']) * C),
        axis=1)
    qualified = qualified.sort_values('wr', ascending=False).head(20)
    return list(qualified['id'])


def present(title):
    passed_title = " ".join(title.lstrip().rstrip().split()).title()
    if passed_title in indices:
        temp = indices[passed_title]
        if isinstance(temp, pd.Series):
            temp = temp[0]
        temp = md.iloc[temp]['id']
    else:
        temp = ''
    return temp


def get_suggestions():
    return list(md['title'].str.capitalize())


def top_picks():
    return top_pick
