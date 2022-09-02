# Simple And Content-Based-Movie-Recommender-System

![Python](https://img.shields.io/badge/Python-3.10-blueviolet)
![Framework](https://img.shields.io/badge/Framework-Flask-red)
![Frontend](https://img.shields.io/badge/Frontend-HTML/CSS/JS-pink)
![API](https://img.shields.io/badge/API-TMDB-fcba03)

Content Based Recommender System recommends movies similar to the movie user likes.

The details of the movies(title, genre, runtime, rating, poster, etc) are fetched using an API by TMDB, https://www.themoviedb.org/documentation/api,

## How to run the project?

1. Clone or download this repository to your local machine.
2. Install all the libraries mentioned in the [requirements.txt](https://github.com/vacom13/MS-project/blob/main/requirements.txt) file with the command `pip install -r requirements.txt`
3. Get your API key from https://www.themoviedb.org/. (Refer the above section on how to get the API key)
3. Replace TMDB_API_KEY in the `app.py` with your own on line no. 8 hit save.
4. Open your terminal/command prompt from your project directory and run the file `app.py` by executing the command `python app.py`.
5. Go to your browser and type `http://127.0.0.1:5000/` in the address bar.
   
## Simple Recommender
Used the IMDB's weighted rating formula to construct the chart. Mathematically, it is represented as follows:

Weighted Rating `(WR) =  (vv+m.R)+(mv+m.C)` 
where,

`v` is the number of votes for the movie
`m` is the minimum votes required to be listed in the chart
`R` is the average rating of the movie
`C` is the mean vote across the whole report
 
## Cosine Similarity for Content Based Recommender
Cosine similarity is a metric used to measure how similar the documents are irrespective of their size. Mathematically, it measures the cosine of the angle between two vectors projected in a multi-dimensional space. The cosine similarity is advantageous because even if the two similar documents are far apart by the Euclidean distance (due to the size of the document), chances are they may still be oriented closer together. The smaller the angle, higher the cosine similarity.
Used the Simple Recommender to improve the content based recommender.
  
![image](https://user-images.githubusercontent.com/36665975/70401457-a7530680-1a55-11ea-9158-97d4e8515ca4.png)


### Source of the datasets 

1. [The Movies Dataset](https://www.kaggle.com/rounakbanik/the-movies-dataset)

### Future scope
- Making the model hybrid between content and collaborative filtering or maybe even use nn.

- Would be better to create an api for accessing the recommendation system separately.

- A database which gets updated with newer movies could be used.

