import pandas as pd
import numpy as np
import requests
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity
from .models import Rating, Favorites, UserContent
from django.core.cache import cache


# Lista de todos los generos

ALL_GENRES = [
    'Action', 'Adventure', 'Animation', 'Comedy', 'Crime',
    'Documentary', 'Drama', 'Family', 'Fantasy', 'History',
    'Horror', 'Mystery', 'Romance', 'Science Fiction',
    'Thriller', 'War', 'Western'
]

# Diccionario con todos los id de peliculas y series organizados

GENRE_IDS = {
    'Action':           {'movie': 28,    'tv': 10759},
    'Adventure':        {'movie': 12,    'tv': 10759},
    'Animation':        {'movie': 16,    'tv': 16},
    'Comedy':           {'movie': 35,    'tv': 35},
    'Crime':            {'movie': 80,    'tv': 80},
    'Documentary':      {'movie': 99,    'tv': 99},
    'Drama':            {'movie': 18,    'tv': 18},
    'Family':           {'movie': 10751, 'tv': 10751},
    'Fantasy':          {'movie': 14,    'tv': 10765},
    'History':          {'movie': 36,    'tv': 36},
    'Horror':           {'movie': 27,    'tv': 27},
    'Mystery':          {'movie': 9648,  'tv': 9648},
    'Romance':          {'movie': 10749, 'tv': 10749},
    'Science Fiction':  {'movie': 878,   'tv': 10765},
    'Thriller':         {'movie': 53,    'tv': 53},
    'War':              {'movie': 10752, 'tv': 10768},
    'Western':          {'movie': 37,    'tv': 37},
}


# Funcion que devuelve los titulos de los id
GENRE_IDS_REVERSE = {}
for name, types in GENRE_IDS.items():
    for content_type, gid in types.items():
        GENRE_IDS_REVERSE[gid] = name


# Filtrado para obtencion de generos
def get_genres_from_tmdb(tmdb_id, media_type):

    cache_key = f"genres_{media_type}_{tmdb_id}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached
  
    if media_type == 'movie':
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    else:
        url = f"https://api.themoviedb.org/3/tv/{tmdb_id}"

    try:
        response = requests.get(url, params={
            'api_key': settings.TMDB_API_KEY,
            'language': 'en-US'
        })

        data = response.json()
        genres = [g['name'] for g in data.get('genres', [])]
        cache.set(cache_key, genres, 60 * 60 * 24)
        return genres

    except Exception as e:
        print(f"Error obteniendo generos {e}")
        return []

#  Buscar contenido en TMDB por género. Devuelve lista de películas/series con sus géneros.
def fetch_by_genre(genre_name, media_type='all'):
  
    results = []

    type_to_fetch = []
    if media_type == 'movie':
        type_to_fetch = ['movie']
    elif media_type == 'tv':
        type_to_fetch = ['tv']
    else:
        type_to_fetch = ['movie', 'tv']

    for content_type in type_to_fetch:

        genre_id = GENRE_IDS.get(genre_name, {}).get(content_type)
        if not genre_id:
            continue

        try:
            response = requests.get(
                f"https://api.themoviedb.org/3/discover/{content_type}",
                params={
                    'api_key': settings.TMDB_API_KEY,
                    'with_genres': genre_id,
                    'language': 'en-US',
                    'sort_by': 'popularity.desc',
                    'page': 1
                }
            )

            data = response.json().get('results', [])

            for item in data[:10]:

                genre_names = [
                    GENRE_IDS_REVERSE.get(gid, '')
                    for gid in item.get('genre_ids', [])
                ]

                genre_names = [g for g in genre_names if g]

                results.append({
                    'id': item.get('id'),
                    'title': item.get('title') or item.get('name'),
                    'poster_path': item.get('poster_path'),
                    'backdrop_path': item.get('backdrop_path'),
                    'vote_average': item.get('vote_average', 0),
                    'media_type': content_type,
                    'genre_names': genre_names,
                    'genre_ids': item.get('genre_ids', [])
                })

        except Exception as e:
            print(f"Error fetching {content_type} for genre {genre_name}: {e}")
            continue


    return results

# Filtrar contenido popular cuando el usuario no tiene suficiente historial para generar un perfil de gustos.
def get_popular_fallback(media_type='all', limit=20):
   
    results = []
    types_to_fetch = ['movie', 'tv'] if media_type == 'all' else [media_type]

    for content_type in types_to_fetch:
        try:
            response = requests.get(
                f"https://api.themoviedb.org/3/{content_type}/popular",
                params={
                    'api_key': settings.TMDB_API_KEY,
                    'language': 'en-US',
                    'page': 1
                }
            )

            data = response.json().get('results', [])

            for item in data:
                genre_names = [
                    GENRE_IDS_REVERSE.get(gid, '')
                    for gid in item.get('genre_ids', [])
                ]

                genre_names = [g for g in genre_names if g]

                results.append({
                    'id': item.get('id'),
                    'title': item.get('title') or item.get('name'),
                    'poster_path': item.get('poster_path'),
                    'backdrop_path': item.get('backdrop_path'),
                    'vote_average': item.get('vote_average', 0),
                    'media_type': content_type,
                    'genre_names': genre_names,
                })
        except Exception as e:
            print(f"Error fetch popular {content_type}: {e}")
            continue

    
    return results[:limit]


# Analiza lo que le gusta al usuario y devuelve un 'vector' con el peso de cada género.
def get_user_genre_profile(user):
    """
    Ejemplo de resultado:
    {'Action': 0.62, 'Comedy': 0.0, 'Horror': 0.0, ...}
    """
    genre_scores = {genre: 0.0 for genre in ALL_GENRES}

    # 1. Favoritos → peso alto (x3)
    favorites = Favorites.objects.filter(user=user)
    for fav in favorites:
        genres = get_genres_from_tmdb(fav.tmdb_id, fav.media_type)
        for genre in genres:
            if genre in genre_scores:
                genre_scores[genre] += 3.0

    # 2. Ratings con escala 1-5 estrellas
    # recorre 'genres' (la lista), no 'genre_scores' (el diccionario)
    all_ratings = Rating.objects.filter(user=user)
    for rating in all_ratings:
        content = UserContent.objects.filter(
            user=user, tmdb_id=rating.tmdb_id
        ).first()

        if content:
            genres = get_genres_from_tmdb(rating.tmdb_id, content.media_type)
            for genre in genres:
                if genre in genre_scores:
                    if rating.value >= 4:
                        genre_scores[genre] += rating.value
                    elif rating.value == 3:
                        pass
                    elif rating.value <= 2:
                        genre_scores[genre] -= rating.value

    # 3. Contenido completado → peso normal (x1)
    completed = UserContent.objects.filter(user=user, status="completed")
    for item in completed:
        genres = get_genres_from_tmdb(item.tmdb_id, item.media_type)
        for genre in genres:
            if genre in genre_scores:
                genre_scores[genre] += 1.0

    # Normalizar los valores (quitar negativos antes de normalizar)
    values = np.array(list(genre_scores.values()))
    values = np.clip(values, 0, None)

    if values.sum() > 0:
        values = values / values.sum()

    return dict(zip(ALL_GENRES, values))

#  Generar recomendaciones personalizadas para el usuario.
def get_recommendations(user, media_type='all', genre_filter=None, min_rating=0, limit=20):
    """
    Parámetros (filtros):
        media_type:   'movie', 'tv', o 'all'
        genre_filter: nombre de un género específico, ej. 'Horror' (opcional)
        min_rating:   calidad mínima en TMDB, ej. 7.5 (opcional)
        limit:        cuántos resultados devolver
    """

    # Perfil del usuario 
    user_profile = get_user_genre_profile(user)

    if all(v == 0.0 for v in user_profile.values()):
        return get_popular_fallback(media_type, limit)

    user_vector = np.array(list(user_profile.values())).reshape(1, -1)

    # Elegir géneros a buscar 
    if genre_filter:
        # Si piden un género específico, solo usa ese
        top_genres = [(genre_filter, user_profile.get(genre_filter, 1.0))]
    else:
        # Si no, usa el top 4 de géneros del usuario
        top_genres = sorted(
            user_profile.items(),
            key=lambda x: x[1],
            reverse=True
        )[:4]

    candidates = []
    for genre_name, score in top_genres:
        if score == 0 and genre_filter is None:
            continue
        candidates.extend(fetch_by_genre(genre_name, media_type))

    # Quitar ya vistos y duplicados
    seen_ids = set(
        UserContent.objects.filter(user=user).values_list('tmdb_id', flat=True)
    )

    unique = {}
    for item in candidates:
        if item['id'] not in seen_ids:
            unique[item['id']] = item

    candidates = list(unique.values())

    if not candidates:
        return get_popular_fallback(media_type, limit)

    #  Pandas para organizar los datos
    df = pd.DataFrame(candidates)

    def build_genre_vector(genre_list):
        vector = {genre: 0.0 for genre in ALL_GENRES}
        for genre in genre_list:
            if genre in vector:
                vector[genre] = 1.0
        return list(vector.values())

    df['genre_vector'] = df['genre_names'].apply(build_genre_vector)

    content_matrix = np.array(df['genre_vector'].tolist())

    # Scikit-learn calcula similitud con la funcion cosine_similarity
    similarities = cosine_similarity(user_vector, content_matrix)[0]
    df['similarity'] = similarities

    # Filtro de calidad mínima 
    if min_rating > 0:
        df = df[df['vote_average'] >= min_rating]

    if df.empty:
        return get_popular_fallback(media_type, limit)

    # Ordenar y devolver 
    df = df.sort_values(
        ['similarity', 'vote_average'],
        ascending=[False, False]
    )

    return df.head(limit).to_dict('records')