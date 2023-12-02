from ..testdata.es_data import es_films_data, es_genres_data


FILMS_RESPONSE_DATA = [
    {
        'uuid': es_film_data['id'],
        'title': es_film_data['title'],
        'imdb_rating': es_film_data['imdb_rating'],
        'description': es_film_data['description'],
        'genres': [{
            'uuid': genre['id'],
            'name': genre['name']
        } for genre in es_film_data['genres']],
        'actors': [{
            'id': actor['id'],
            'name': actor['name']
        } for actor in es_film_data['actors']],
        'writers': [{
            'id': writer['id'],
            'name': writer['name']
        } for writer in es_film_data['writers']],
        'directors': [{
            'id': director['id'],
            'name': director['name']
        } for director in es_film_data['directors']],
    } for es_film_data in es_films_data
]


FILMS_SHORT_RESPONSE_DATA = [
    {
        'uuid': es_film_data['id'],
        'title': es_film_data['title'],
        'imdb_rating': es_film_data['imdb_rating']
    } for es_film_data in es_films_data]

GENRES_RESPONSE_DATA = [
    {
        'uuid': genre['id'],
        'name': genre['name']
    } for genre in es_genres_data]

HTTP_200 = 200
HTTP_404 = 404
HTTP_422 = 422
