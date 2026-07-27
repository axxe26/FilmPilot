import json

from .models import UserContent, UserProfile, WatchList
from .models import WatchedEpisode
from .models import WatchedSeason
from .models import WatchedMovie
from .models import Rating
from .models import Favorites


import requests
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Count
from django.contrib import messages

from django.contrib.auth.models import User
from django.shortcuts import render, redirect 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect



from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .recommendations import get_recommendations, get_user_genre_profile 


# Diccionario de generos
GENRES = {
    28: 'Action',
    12: 'Adventure',
    16: 'Animation',
    35: 'Comedy',
    80: 'Crime',
    99: 'Documentary',
    18: 'Drama',
    10751: 'Family',
    14: 'Fantasy',
    36: 'History',
    27: 'Horror',
    9648: 'Mystery',
    10749: 'Romance',
    878: 'Science Fiction',
    10770: 'TV Movie',
    53: 'Thriller',
    10752: 'War',
    37: 'Western',
    10402: 'Music'
}


# Diccionario de genero TV
TV_GENRES = {
    10759: "Action & Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    10762: "Kids",
    9648: "Mystery",
    10763: "News",
    10764: "Reality",
    10765: "Sci-Fi & Fantasy",
    10766: "Soap",
    10767: "Talk",
    10768: "War & Politics",
    37: "Western",
}

# Dicionario de id en generos en comun entre pelicula y series
COMMON_GENRES = {
    1: {
        'name': 'Action',
        'movie_id': 28,
        'tv_id': 10759
    },

    2: {
        'name': 'Comedy',
        'movie_id': 35,
        'tv_id': 35
    },

    3: {
        'name': 'Crime',
        'movie_id': 80,
        'tv_id': 80
    },

    4: {
        'name': 'Drama',
        'movie_id': 18,
        'tv_id': 18
    },

    5: {
        'name': 'Family',
        'movie_id': 10751,
        'tv_id': 10751
    },

    6: {
        'name': 'Horror',
        'movie_id': 27,
        'tv_id': 9648
    },

    7: {
        'name': 'Romance',
        'movie_id': 10749,
        'tv_id':  18
    },

    8: {
        'name': 'Science Fiction',
        'movie_id': 878,
        'tv_id': 10765
    },


}

# Filtrado de Landing Page (top 10 movie, to 10 series, genres)
def home(request):

    # URLs base de TMDB 
    url_movies = "https://api.themoviedb.org/3/movie/popular"
    url_tv = "https://api.themoviedb.org/3/tv/popular"

    # Parámetros de autenticación e idioma.
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US',
        'page': 1
    }
    try:
       movies_response = requests.get(url_movies, params=params)
       tv_response = requests.get(url_tv, params=params)

       movies = movies_response.json().get('results',[])[:10]
       tv_series = tv_response.json().get('results',[])[:10]
                                           
    except requests.exceptions.RequestException as e:
        print(f"Error fetching popular movies: {e}")
        movies = [] 
        tv_series = []
    

    for movie in movies:
        movie['genre_names'] = [GENRES.get(id, "") for id in movie.get('genre_ids', [])]

    for tv in tv_series:
        tv['genre_names'] = [GENRES.get(id, "") for id in tv.get('genre_ids', [])]

    genres = []

    for genre_id, genre_data in COMMON_GENRES.items():
        url = f"https://api.themoviedb.org/3/discover/movie"

        params = {
            'api_key': settings.TMDB_API_KEY,
            'with_genres': genre_data['movie_id'],
            'language': 'en-US',
            'page': 1
        }
        # Realiza la consulta a la API.
        try:
            response = requests.get(url, params=params)
            data = response.json().get('results', [])

            if data and data[0].get('backdrop_path'):
                image_url = f"https://image.tmdb.org/t/p/w780{data[0]['backdrop_path']}"
            else:
                image_url = "/static/img/default.jpg"
        
        except:
            image_url = "/static/img/default.jpg"

        genres.append({
            'id': genre_id,
            'name': genre_data['name'],
            'image_url': image_url
        })

    return render(request, 'home.html', 
                  {'movies': movies,
                    'tv_series': tv_series,
                    'genres': genres
    }) 

# Filtrado para genero combinado entre (peliculas y series)
# Filtro de generos de movie
def movies_by_genre(request, genre_id):
    url = f"https://api.themoviedb.org/3/discover/movie"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'with_genres': genre_id,
        'language': 'en-US',
        'page': 1
    }
    
    try:
        res = requests.get(url, params=params)
        movies = res.json().get('results', [])
    except:
        movies = []
    
    genre_name = GENRES.get(genre_id, "Unknown Genre")

    return render(request, 'movies_by_genre.html', {
        'movies': movies, 
        'genre_name': genre_name
    })

# Filtro de generos de tv
def tv_series_by_genre(request, genre_id):
    url = f"https://api.themoviedb.org/3/discover/tv"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'with_genres': genre_id,
        'language': 'en-US',
        'page': 1
    }

    try:
        res = requests.get(url, params=params)
        tv_series = res.json().get('results', [])
    except:
        tv_series = []

    genre_name = GENRES.get(genre_id, "Unknown Genre")

    return render(request, 'tv_series_by_genre.html', {
        'tv_series': tv_series,
        'genre_name': genre_name
    })

# Filtrado de genero combinado de movie y serie
def genre_combined(request, genre_id):
    url_movies = f"https://api.themoviedb.org/3/discover/movie"
    url_tv = f"https://api.themoviedb.org/3/discover/tv"

    params = {
        'api_key': settings.TMDB_API_KEY,
        'with_genres': genre_id,
        'language': 'en-US',
        'page': 1
    }

    try:
        movies_response = requests.get(url_movies, params=params)
        tv_response = requests.get(url_tv, params=params)

        movies = movies_response.json().get('results', [])
        tv_series = tv_response.json().get('results', [])

    except:
        movies = []
        tv_series = []  
    
    combined = []

    for movie in movies:
        movie['type'] = 'movie'
        combined.append(movie)
    
    for tv in tv_series:
        tv['type'] = 'tv'
        combined.append(tv)
    
    genre_name = GENRES.get(genre_id, "Unknown Genre")

    return render(request, 'genre_combined.html', {
        'movies': movies,
        'tv_series': tv_series,
        'combined': combined,
        'genre_name': genre_name
    })

# Obtener películas y series de un género específico.
def get_content_by_genre(request, genre_id):

    genre = COMMON_GENRES.get(genre_id)

    if not genre:
        return JsonResponse([], safe=False)
    
    url_movies = f"https://api.themoviedb.org/3/discover/movie"
    url_tv = f"https://api.themoviedb.org/3/discover/tv"

    movie_params = {
        'api_key': settings.TMDB_API_KEY,
        'with_genres': genre['movie_id'],
        'language': 'en-US',
        'page': 1
    }

    tv_params = {
        'api_key': settings.TMDB_API_KEY,
        'with_genres': genre['tv_id'],
        'language': 'en-US',
        'page': 1
    }

    try:
        movies = requests.get(url_movies, params=movie_params).json().get('results', [])[:6]

        tv_series = requests.get(url_tv, params=tv_params).json().get('results', [])[:6]
    
    except Exception as e:
        print(f"Error occurred: {e}")
        movies = []
        tv_series = []

    combined = []


    max_length = max(len(movies), len(tv_series))

    for i in range(max_length):

        if i < len(movies):

            movie = movies[i]

            combined.append({

                'id': movie.get('id'),
                'title': movie.get('title'),
                'poster_path': movie.get('poster_path'),
                'backdrop_path': movie.get('backdrop_path'),
                'overview': movie.get('overview'),
                'vote_average': movie.get('vote_average'),
                'release_date': movie.get('release_date'),
                'media_type': 'movie'
            })

        if i < len(tv_series):

            tv = tv_series[i]

            combined.append({

                'id': tv.get('id'),
                'title': tv.get('name'),
                'poster_path': tv.get('poster_path'),
                'backdrop_path': tv.get('backdrop_path'),
                'overview': tv.get('overview'),
                'vote_average': tv.get('vote_average'),
                'release_date': tv.get('first_air_date'),
                'media_type': 'tv'
            })
        
    combined = combined[:6]

    return JsonResponse(combined, safe=False)

# Funcion para registro de la pagina 
def register(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('home')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('home')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('home')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        UserProfile.objects.create(
            user=user,
            profile_picture=request.FILES.get('profile_picture'),
            about_me=request.POST.get('about_me', ''),
            recommendations=("recommendation" in request.POST),
            newsletter=("newsletter" in request.POST)
        )

        messages.success(request, 'Account created successfully')
        return redirect('home')

    return redirect('home') 

# Funcion para poder loguearse luego del registro
def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        from django.contrib.auth import authenticate, login as auth_login

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')

        else:
            messages.error(request, "Invalid username or password")
            return redirect('home')

    return redirect('home')


# Contenido principal de la app (contenido generico, popular, mi contenido, detalles, recomendaciones inteligentes, estadisticas)
@login_required
def dashboard(request):

    url_movies = "https://api.themoviedb.org/3/movie/popular"
    url_tv = "https://api.themoviedb.org/3/tv/popular"
    trending_movies = get_trending_movies()
    trending_tv = get_trending_tv_shows()
    user = request.user

    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US',
        'page': 1
    }

    # Trae películas y series populares (página 1) desde TMDB
    movies = requests.get(url_movies, params=params).json().get('results', [])
    tv_series = requests.get(url_tv, params=params).json().get('results', [])

     # Combina películas y series en una sola lista y se queda con las primeras 10
    combined = combine_content(movies, tv_series)[:10]

    # Convierte los genre_ids de cada item en un string legible"
    for item in combined:
        item["genres"] = " • ".join(
            GENRES.get(genre_id, "")
            for genre_id in item.get("genre_ids", [])
            if GENRES.get(genre_id)
        )
    
    # Series que el usuario está viendo actualmente
    currently_waching_qs = UserContent.objects.filter (
        user=request.user,
        media_type="tv",
        status="watching"
    )

    currently_watching = []

    for item in currently_waching_qs:
        episode_count = WatchedEpisode.objects.filter(
            user=request.user,
            tmdb_id=item.tmdb_id
        ).count()

        try:
            res = requests.get(
                f"https://api.themoviedb.org/3/tv/{item.tmdb_id}",
                params={"api_key": settings.TMDB_API_KEY, "language": "en-US"}
            )

            data = res.json()
            total_episodes = data.get("number_of_episodes", 0)

        except:
            total_episodes = 0

        currently_watching.append({
            "tmdb_id": item.tmdb_id,
            "name": item.title,
            "poster_path": item.poster_path,
            "episodes_watched": episode_count,
            "total_episodes": total_episodes
        })

    # Series marcadas como completadas por el usuario
    completed_qs = UserContent.objects.filter(
        user=request.user,
        media_type="tv",
        status="completed"
    ) 

    completed_series = []

    for item in completed_qs:

        episode_count = WatchedEpisode.objects.filter(
            user=request.user,
            tmdb_id=item.tmdb_id
        ).count()

        try:
            res = requests.get(
                 f"https://api.themoviedb.org/3/tv/{item.tmdb_id}",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "language": "en-US"
                }
            )
        
            data = res.json()

            completed_series.append({
                "tmdb_id": item.tmdb_id,
                "name": item.title,
                "poster_path": item.poster_path,
                "episodes_watched": episode_count,
                "total_episodes": data.get("number_of_episodes", 0)
            })
        except:
            pass


    # Películas marcadas como completadas       
    completed_movies_qs = UserContent.objects.filter(
        user=request.user,
        media_type="movie",
        status="completed"
    ) 

    completed_movies= []

    for item in completed_movies_qs:
        completed_movies.append({
            "tmdb_id": item.tmdb_id,
            "title": item.title,
            "poster_path": item.poster_path,
        })

     # Watchlist del usuario
    watchList_qs = WatchList.objects.filter(user=request.user)
    watchList_items = []

    for item in watchList_qs:
        try:
            res = requests.get(
                f"https://api.themoviedb.org/3/{item.media_type}/{item.tmdb_id}",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "language": "en-US"
                }
            )
            
            data = res.json()

            watchList_items.append({
                "tmdb_id": item.tmdb_id,
                "media_type": item.media_type,
                "title": data.get("title") or data.get("name"),
                "poster_path": data.get("poster_path"),
                "vote_average": data.get("vote_average"),
                "release_date": data.get("release_date") or data.get("first_air_date") 
            })

        except:
            pass
    # Favoritos del usuario: mismo patrón que el watchlist de arriba
    favorites_qs = Favorites.objects.filter(user=request.user)
    favorites_items = []

    for item in favorites_qs:
        try:
            res = requests.get(
                f"https://api.themoviedb.org/3/{item.media_type}/{item.tmdb_id}",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "language": "en-US"
                }
            )
            
            data = res.json()

            favorites_items.append({
                "tmdb_id": item.tmdb_id,
                "media_type": item.media_type,
                "title": data.get("title") or data.get("name"),
                "poster_path": data.get("poster_path"),
                "vote_average": data.get("vote_average"),
                "release_date": data.get("release_date") or data.get("first_air_date") 
            })

        except:
            pass
    
    # Recomendaciones personalizadas según el perfil del usuario 
    recommended_all = get_recommendations(request.user, media_type='all', limit=15)

    recommended_movies = get_recommendations(request.user, media_type='movie', limit=15)

    recommended_series = get_recommendations(request.user, media_type='tv', limit=15)

    recommended_top_rated = get_recommendations(request.user, min_rating=7.5, limit=15)


    # actividad reciente
    recent_activity = []


    # Últimas 10 películas vistas
    watched_movies = WatchedMovie.objects.filter(
        user=request.user
    ).order_by('-watched_at')[:10]

    for item in watched_movies:
        recent_activity.append({
            'type': 'watched',
            'emoji': '🎬',
            'action': 'You watched',
            'title': item.title,
            'poster_path': UserContent.objects.filter(
                user=request.user, tmdb_id=item.tmdb_id
            ).values_list('poster_path', flat=True).first() or '',
            'tmdb_id': item.tmdb_id,
            'media_type': 'movie',
            'date': item.watched_at,
        })

    # Últimos 10 favoritos agregados
    recent_favorites = Favorites.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    for item in recent_favorites:
        
        title = item.title
        poster_path = item.poster_path
        if not title or not poster_path:
            content = UserContent.objects.filter(
                user=request.user, tmdb_id=item.tmdb_id
            ).first()
            if content:
                title = title or content.title
                poster_path = poster_path or content.poster_path

        if title:
            recent_activity.append({
                'type': 'favorite',
                'emoji': '❤️',
                'action': 'You favorited',
                'title': title,
                'poster_path': poster_path,
                'tmdb_id': item.tmdb_id,
                'media_type': item.media_type,
                'date': item.created_at,
            })

    # Últimos 10 agregados al watchlist
    recent_watchlist = WatchList.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    for item in recent_watchlist:
        title = item.title
        poster_path = item.poster_path
        if not title or not poster_path:
            content = UserContent.objects.filter(
                user=request.user, tmdb_id=item.tmdb_id
            ).first()
            if content:
                title = title or content.title
                poster_path = poster_path or content.poster_path

        if title:
            recent_activity.append({
                'type': 'watchlist',
                'emoji': '🔖',
                'action': 'Added to watchlist',
                'title': title,
                'poster_path': poster_path,
                'tmdb_id': item.tmdb_id,
                'media_type': item.media_type,
                'date': item.created_at,
            })

    # Últimas 10 calificaciones (ratings)
    recent_ratings = Rating.objects.filter(
        user=request.user
    ).order_by('-updated_at')[:10]

    for item in recent_ratings:
        title = item.title
        poster_path = item.poster_path
        media_type = item.media_type
        if not title or not poster_path:
            content = UserContent.objects.filter(
                user=request.user, tmdb_id=item.tmdb_id
            ).first()
            if content:
                title = title or content.title
                poster_path = poster_path or content.poster_path
                media_type = media_type or content.media_type

        if title:
            recent_activity.append({
                'type': 'rating',
                'emoji': '⭐',
                'action': f'You rated',
                'title': title,
                'poster_path': poster_path,
                'tmdb_id': item.tmdb_id,
                'media_type': media_type,
                'date': item.updated_at,
                'rating': item.value,
                'stars_active': item.value,          
                'stars_inactive': 5 - item.value,    
            })

     # Ordena toda la actividad (de los 4 tipos combinados) por fecha desc y se queda con las 20 más recientes
    recent_activity = sorted(
        recent_activity,
        key=lambda x: x['date'],
        reverse=True
    )[:20]


    # Estadísticas generales del usuario para el dashboard 

    total_movies_watched = WatchedMovie.objects.filter(user=request.user).count()

    total_episodes_watched = WatchedEpisode.objects.filter(user=request.user).count()

    series_watching = UserContent.objects.filter(
        user=request.user,
        media_type="tv",
        status="watching"
    )

    total_series_watching = series_watching.count()

     # Calcula cuántos episodios le faltan al usuario en total, sumando entre todas sus series "watching"
    total_episodes_remaining = 0

    for serie in series_watching:
        try:
            res = requests.get(
                f"https://api.themoviedb.org/3/tv/{serie.tmdb_id}",
                params={
                    "api_key": settings.TMDB_API_KEY,
                    "language": "en-US"
                }
            )
            data = res.json()
            total_episodes = data.get("number_of_episodes", 0)
            watched_episodes = WatchedEpisode.objects.filter(
                user=request.user,
                tmdb_id=serie.tmdb_id
            ).count()
            total_episodes_remaining += max(0, total_episodes - watched_episodes)
        except:
            continue

    total_series_completed = UserContent.objects.filter(
        user=request.user,
        media_type="tv",
        status="completed"
    ).count()

    total_favorites = Favorites.objects.filter(user=request.user).count()

    total_watchlist = WatchList.objects.filter(user=request.user).count()
    # Promedio de todas las calificaciones que puso el usuario
    all_ratings = Rating.objects.filter(user=request.user)
    if all_ratings.exists():
        average_rating = round(sum(r.value for r in all_ratings) / all_ratings.count(), 1)

    else:
        average_rating = 0
    # Perfil de géneros del usuario (basado en su historial/gustos) para el gráfico de géneros favoritos
    user_profile = get_user_genre_profile(request.user)

    # Se queda con los top 5 géneros según el score
    top_genres = sorted(
        user_profile.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    genre_labels = [genre for genre, score in top_genres if score > 0]
    genre_counts = [round(score * 100, 1) for genre, score in top_genres if score > 0]

    # Cuenta cuántos items tiene el usuario en cada estado (para el gráfico de estados)
    status_counts = {
        'Watching':  UserContent.objects.filter(user=request.user, status='watching').count(),
        'Completed': UserContent.objects.filter(user=request.user, status='completed').count(),
        'Planned':   UserContent.objects.filter(user=request.user, status='planned').count(),
        'Dropped':   UserContent.objects.filter(user=request.user, status='dropped').count(),
    }

    status_labels = list(status_counts.keys())
    status_data   = list(status_counts.values())

    # Renderiza el template del dashboard con todo lo visto arriba
    return render(request, 'dashboard.html', {
        'combined': combined,
        'movies': movies,
        'tv_series': tv_series,
        'trending_movies':trending_movies,
        'trending_tv': trending_tv,
        'user': user,
        'genres': GENRES,
        'tv_genres': TV_GENRES,
        'currently_watching': currently_watching,
        'completed_series': completed_series,
        'completed_movies': completed_movies,
        'watchlist_items': watchList_items,
        'favorites_items': favorites_items,
        'recommended_all': recommended_all,
        'recommended_movies': recommended_movies,
        'recommended_tv': recommended_series,
        'recommended_top_rated': recommended_top_rated,
        'recent_activity': recent_activity,
        'stats': {
            'movies_watched': total_movies_watched,
            'total_episodes_watched': total_episodes_watched,
            'total_episodes_remaining': total_episodes_remaining,
            'total_series_completed': total_series_completed,
            'series_watching': total_series_watching,
            'total_favorites': total_favorites,
            'total_watchlist': total_watchlist,
            'average_rating': average_rating
        },
        "genre_labels": genre_labels,
        "genre_counts": genre_counts,
        "status_labels": status_labels,
        "status_data": status_data,
    })


# Combinar peliculas y series en una sola lista 
def combine_content(movies, tv_series):
    combined = []
    # Obtener la longitud maxima entre ambas listas
    max_length = max(len(movies), len(tv_series))
    # Recorrer ambas listas y alternar las peliculas y series
    for i in range(max_length):

        if i < len(movies):
            movies[i]['media_type'] = 'movie'
            combined.append(movies[i])

        if i < len(tv_series):
            tv_series[i]['media_type'] = 'tv'
            combined.append(tv_series[i])
    # Devolver lista combinada
    return combined


# Filtra peliculas en tendencia de la semana
def get_trending_movies():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={settings.TMDB_API_KEY}"
    response = requests.get(url)
    return response.json().get("results",[])

# Filtra series en tendencia de la semana
def get_trending_tv_shows():
    url = f"https://api.themoviedb.org/3/trending/tv/week?api_key={settings.TMDB_API_KEY}"
    response = requests.get(url)
    return response.json().get("results",[])



def global_search(request):
    """
    Búsqueda genérica para la barra del Home: combina resultados de
    películas y series (marcando cuáles son anime) en una sola lista,
    ordenada por popularidad.
    """

    # Obtiene el texto ingresado por el usuario

    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
        "query": query,
    }

    results = []

    try:
        movie_res = requests.get(
            "https://api.themoviedb.org/3/search/movie", params=params
        )
        if movie_res.status_code == 200:
            for item in movie_res.json().get("results", []):
                if not item.get("poster_path"):
                    continue
                results.append({
                    "id": item.get("id"),
                    "media_type": "movie",
                    "is_anime": False,
                    "title": item.get("title"),
                    "poster_path": item.get("poster_path"),
                    "release_date": item.get("release_date") or "",
                    "popularity": item.get("popularity", 0),
                })
    except Exception:
        pass

    try:
        tv_res = requests.get(
            "https://api.themoviedb.org/3/search/tv", params=params
        )
        if tv_res.status_code == 200:
            for item in tv_res.json().get("results", []):
                if not item.get("poster_path"):
                    continue

                genre_ids = item.get("genre_ids", [])
                origin = item.get("origin_country", [])
                is_anime = 16 in genre_ids and "JP" in origin

                results.append({
                    "id": item.get("id"),
                    "media_type": "tv",
                    "is_anime": is_anime,
                    "title": item.get("name"),
                    "poster_path": item.get("poster_path"),
                    "release_date": item.get("first_air_date") or "",
                    "popularity": item.get("popularity", 0),
                })
    except Exception:
        pass
    # Ordena los resultados por popularidad y devuelve los primeros 12
    results.sort(key=lambda x: x["popularity"], reverse=True)

    return JsonResponse({"results": results[:12]})

# Filtrar peliculas segun las peticiones del usuario
def filter_movies(request):

    genre = request.GET.get("genre")
    popularity = request.GET.get("popularity")
    release_date = request.GET.get("release_date")
    upcoming = request.GET.get("upcoming")
    search = request.GET.get("search")

    today = date.today()

    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US',

    }

    if genre:
        params["with_genres"] = genre

    if popularity == "desc":
        params["sort_by"] = "popularity.desc"

    elif popularity == "asc":
        params["sort_by"] = "popularity.asc"

    if release_date == "newest":
        params["sort_by"] = "primary_release_date.desc"

    elif release_date == "oldest":
        params["sort_by"] = "primary_release_date.asc"

    if upcoming == "soon":

        params["primary_release_date.gte"] = today.strftime("%Y-%m-%d")

        params["primary_release_date.lte"] = (
            today + timedelta(days=30)
        ).strftime("%Y-%m-%d")

    elif upcoming == "later":

        params["primary_release_date.gte"] = (
            today + timedelta(days=31)
        ).strftime("%Y-%m-%d")

    url = "https://api.themoviedb.org/3/discover/movie"

    if search:
        url = "https://api.themoviedb.org/3/search/movie"
        params["query"] = search


    all_movies = []

    for page_num in range(1, 10):

        params["page"] = page_num

        response = requests.get(url, params=params)

        if response.status_code == 200:

            all_movies.extend(
                response.json().get("results", [])
            )

        else:
            print(
                f"Error en página {page_num}: "
                f"{response.status_code}"
            )

    return JsonResponse({
        "results": all_movies
    })


# Filtrar series segun las peticiones del usuario
def filter_tv(request):

    genre = request.GET.get("genre")
    popularity = request.GET.get("popularity")
    release_date = request.GET.get("release_date")
    upcoming = request.GET.get("upcoming")
    search = request.GET.get("search")

    today = date.today()

    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US',

    }

    if genre:
        params["with_genres"] = genre

    if popularity == "desc":
        params["sort_by"] = "popularity.desc"

    elif popularity == "asc":
        params["sort_by"] = "popularity.asc"

    if release_date == "newest":
        params["sort_by"] = "primary_release_date.desc"

    elif release_date == "oldest":
        params["sort_by"] = "primary_release_date.asc"

    if upcoming == "soon":

        params["primary_release_date.gte"] = today.strftime("%Y-%m-%d")

        params["primary_release_date.lte"] = (
            today + timedelta(days=30)
        ).strftime("%Y-%m-%d")

    elif upcoming == "later":

        params["primary_release_date.gte"] = (
            today + timedelta(days=31)
        ).strftime("%Y-%m-%d")

    url = "https://api.themoviedb.org/3/discover/tv"

    if search:
        url = "https://api.themoviedb.org/3/search/tv"
        params["query"] = search


    all_tv = []

    for page_num in range(1, 10):

        temp_params = params.copy()
        temp_params["page"] = page_num

        response = requests.get(url, params=temp_params)

        if response.status_code == 200:

            all_tv.extend(
                response.json().get("results", [])
            )

        else:
            print(
                f"Error en página {page_num}: "
                f"{response.status_code}"
            )

    return JsonResponse({
        "results": all_tv
    })

# Filtrar series segun las peticiones del usuario
def anime_filter(request):

    genre = request.GET.get("genre")
    popularity = request.GET.get("popularity")
    release_date = request.GET.get("release_date")
    status = request.GET.get("status")
    search = request.GET.get("search")

    base_params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
    }


    # Modo a buscar
    
    if search:
        url = "https://api.themoviedb.org/3/search/tv"
        params = {
            **base_params,
            "query": search
        }

    # Buscador de anime

    else:
        url = "https://api.themoviedb.org/3/discover/tv"
        params = {
            **base_params,
            "with_genres": 16,
            "with_origin_country": "JP",
        }

        # Invalidar genero 
        if genre and genre != "anime":
            params["with_genres"] = genre

        # Popularida
        if popularity == "asc":
            params["sort_by"] = "popularity.asc"
        elif popularity == "desc":
            params["sort_by"] = "popularity.desc"

        # Lanzamiento date
        if release_date == "newest":
            params["sort_by"] = "first_air_date.desc"
        elif release_date == "oldest":
            params["sort_by"] = "first_air_date.asc"

        # Estado (simulado)
        if status == "ongoing":
            params["first_air_date.gte"] = "2022-01-01"

        elif status == "completed":
            params["first_air_date.lte"] = "2020-12-31"

    
    # Paginacion (division de contenido)
    all_anime = []

    for page_num in range(1, 10):

        temp_params = params.copy()
        temp_params["page"] = page_num

        response = requests.get(url, params=temp_params)

        if response.status_code == 200:
            all_anime.extend(response.json().get("results", []))
        else:
            print(f"Error en página {page_num}: {response.status_code}")

    return JsonResponse({
        "results": all_anime
    })



# Actualizar la informacion del perfil autenticado
def update_profile(request):

    # Procesa unicamente solicitudes de tipo POST
    if request.method == "POST":

        user = request.user
        profile = request.user.userprofile

        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.username = request.POST.get("username")

        profile.about_me = request.POST.get("about_me")

        # Actualizar la foto de perfil si el usuario selecciona una nueva
        if request.FILES.get("profile_picture"):
            profile.profile_picture = request.FILES["profile_picture"]

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")

        # Validar y actualizar la contraseña cuando el usuario solicita un cambio
        if new_password:

            if not user.check_password(current_password):
                messages.error(request,
                               "Current password is incorrect"
                               )
                return redirect("dashboard")
            
            if new_password != confirm_new_password:
                messages.error(
                    request,
                    "Passwords do not match"
                )
                return redirect("dashboard")
            
            user.set_password(new_password)

            # Mantener la sesion activa luego del cambio de contraseña
            update_session_auth_hash(request, user)

        user.save()
        profile.save()

        messages.success(
            request,
            "Profile updated successfully"
        )

    return redirect("dashboard")

# Obtener todos los detalles de peliculas y series
@login_required
def details(request, media_type, tmdb_id):

    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
    providers_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/watch/providers"
    videos_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/videos"
    credits_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/credits"
    similar_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/similar"

    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
    }

    # Detalles de la película/serie
    response = requests.get(url, params=params)
    data = response.json()

    # Plataformas
    providers_response = requests.get(
        providers_url,
        params={"api_key": settings.TMDB_API_KEY}
    )

    providers_data = providers_response.json()

    videos_response = requests.get(videos_url, params=params)
    videos_data = videos_response.json()

    credits_response = requests.get(credits_url, params=params)
    credits_data = credits_response.json()

    cast = credits_data.get("cast",[])[:20]

    similar_response = requests.get(similar_url, params=params)
    similar_data = similar_response.json()

    similar = similar_data.get("results",[])[:15]

    trailer_key = None

    # Intentar trailer oficial
    for video in videos_data.get("results", []):
        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
            and "Official" in video.get("name", "")
        ):
            trailer_key = video["key"]
            break

    # Si no encontró uno oficial, usar cualquier trailer
    if trailer_key is None:
        for video in videos_data.get("results", []):
            if (
                video.get("site") == "YouTube"
                and video.get("type") == "Trailer"
            ):
                trailer_key = video["key"]
                break
    
    seasons = []
    episodes = []

    if media_type == "tv":
        seasons = data.get("seasons", [])
        if seasons:
            
            selected_season = int(
                request.GET.get(
                    "season",
                    seasons[0]["season_number"]
                )
            )

            season_url = (
                f"https://api.themoviedb.org/3/tv/"
                f"{tmdb_id}/season/{selected_season}"
            )
            season_response = requests.get (
                season_url,
                params=params
            )

            season_data = season_response.json()

            episodes = season_data.get("episodes", [])


    country = providers_data.get("results", {}).get("DO", {})
    providers = country.get("flatrate", [])

    title = data.get("title") or data.get("name")

    user_rating_obj = Rating.objects.filter(
        user=request.user,
        tmdb_id=tmdb_id,
    ).first()

    watchlist_item= WatchList.objects.filter(
        user=request.user,
        tmdb_id=tmdb_id,
        media_type=media_type
    ).first()

     
    favorite_item=Favorites.objects.filter(
        user=request.user,
        tmdb_id=tmdb_id,
        media_type=media_type
    ).first()

    # Agrupar toda la información del contenido y del usuario que será utilizada
    # para renderizar la página de detalles.
    context = {
        "media_type": media_type,
        "tmdb_id": tmdb_id,

        "title": title,
        "overview": data.get("overview"),
        "poster_path": data.get("poster_path"),
        "backdrop_path": data.get("backdrop_path"),
        "vote_average": data.get("vote_average"),
        "release_date": data.get("release_date") or data.get("first_air_date"),
        "genres": data.get("genres", []),
        "tagline": data.get("tagline"),
        "runtime": data.get("runtime"),
        "number_of_episodes": data.get("number_of_episodes"),
        "trailer_key": trailer_key,

        "providers": providers,
        "cast": cast,
        "similar": similar,
        "seasons": seasons,
        "episodes": episodes,
        "user_rating": user_rating_obj.value if user_rating_obj else 0,
        "in_watchlist": watchlist_item,
        "favorite": favorite_item,
       
    }

    # Enviar informacion al details
    return render(
        request,
        "details.html",
        context
    )

# Filtrar lista de episodios de temporada especifica
def get_season_episodes(request, tmdb_id, season_number):

    url =  f"https://api.themoviedb.org/3/tv/{tmdb_id}/season/{season_number}"

    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
    }
    
    response = requests.get(url, params=params)
    data = response.json()

    return JsonResponse(data.get("episodes", []), safe=False)

# Marcar o desmarca un episodio como visto para el usuario autentificado
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_episode(request):
    user = request.user
    data = request.data

    obj, created = WatchedEpisode.objects.get_or_create(
        user=user,
        tmdb_id=data["tmdb_id"],
        season_number=data["season_number"],
        episode_number=data["episode_number"]
    )

    

    if not created:
        obj.delete()
        return Response({"watched": False})
    
    UserContent.objects.update_or_create(
        user=user,
        tmdb_id=data["tmdb_id"],
        media_type="tv",
        defaults={
            "title": data.get("title", ""),
            "poster_path": data.get("poster_path", ""),
            "status": "watching"
        }
    )

    update_tv_status(user, data["tmdb_id"])

    return Response({"watched":True})

# Marcar o desmarca una temporada como visto para el usuario autentificado
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_season(request):
    user = request.user
    data = request.data

    tmdb_id = data["tmdb_id"]
    season_number = data["season_number"]
    episode_count = int(data["episode_count"])

    season, created = WatchedSeason.objects.get_or_create(
        user=user,
        tmdb_id=tmdb_id,
        season_number=season_number
    )


    if not created:

        season.delete()

        WatchedEpisode.objects.filter(
            user=user,
            tmdb_id=tmdb_id,
            season_number=season_number
        ).delete()

        remaining = WatchedEpisode.objects.filter(
            user=user,
            tmdb_id=tmdb_id
        ).exists()

        if not remaining:
            UserContent.objects.filter(
                user=user,
                tmdb_id=tmdb_id,
                media_type="tv"
            ).delete()

        return Response({"watched": False})


    for episode in range(1, episode_count + 1):
        WatchedEpisode.objects.get_or_create(
            user=user,
            tmdb_id=tmdb_id,
            season_number=season_number,
            episode_number=episode
        )

    UserContent.objects.update_or_create(
        user=user,
        tmdb_id=tmdb_id,
        media_type="tv",
        defaults={
            "title": data.get("title", ""),
            "poster_path": data.get("poster_path", ""),
            "status": "watching"
        }
    )

    update_tv_status(user, tmdb_id)

    return Response({"watched": True})

# Marcar o desmarca una pelicula como visto para el usuario autentificado
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_movie(request):
    user = request.user
    data = request.data
    tmdb_id = data["tmdb_id"]

    obj, created = WatchedMovie.objects.get_or_create(
        user=user,
        tmdb_id=tmdb_id,
    )

    if not created:
        obj.delete()
        UserContent.objects.filter(
            user=user,
            tmdb_id=tmdb_id,
            media_type="movie"
        ).delete()
        return Response({"watched": False})

    # Si no vienen datos del frontend, los busca en TMDB
    poster_path = data.get("poster_path", "")
    title = data.get("title", "")


    if not poster_path or not title:
        try:
            res = requests.get(
                f"https://api.themoviedb.org/3/movie/{tmdb_id}",
                params={"api_key": settings.TMDB_API_KEY, "language": "en-US"}
            )
            tmdb_data = res.json()
            poster_path = poster_path or tmdb_data.get("poster_path", "")
            title = title or tmdb_data.get("title", "")
        except:
            pass

    UserContent.objects.update_or_create(
        user=user,
        tmdb_id=tmdb_id,
        media_type="movie",
        defaults={
            "title": title,
            "poster_path": poster_path,
            "status": "completed"
        }
    )

    return Response({"watched": True})

  
# Verifica si una película ha sido marcada como vista por el usuario

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_movie(request, tmdb_id):
    exists= WatchedMovie.objects.filter(
        user=request.user,
        tmdb_id=tmdb_id,
    ).exists()

    return Response({"watched": exists})

  
# Verifica si el episodio ha sido marcado como vist0 por el usuario
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_episode(request,  tmdb_id, season_number, episode_number):

    exists = WatchedEpisode.objects.filter(
        user=request.user,
        tmdb_id=tmdb_id,
        season_number=season_number,
        episode_number=episode_number
    ).exists()

    return Response({"watched": exists})

  
# Verifica si una temporada ha sido marcada como vista por el usuario
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_season(request, tmdb_id, season_number):

    exists = WatchedSeason.objects.filter(
        user=request.user,
        tmdb_id=tmdb_id,
        season_number=season_number,
    ).exists()

    return Response({"watched": exists})


# Guarda o actualiza la calificación asignada por el usuario a un contenido
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_rating(request):
    data = request.data

    user = request.user
    tmdb_id = data.get("tmdb_id")
    value = data.get("value")
    media_type = data.get("media_type") or "movie"
    title = data.get("title", "")
    poster_path = data.get("poster_path", "")

    if poster_path.startswith("https://image.tmdb.org/t/p/w500"):
        poster_path = poster_path.replace("https://image.tmdb.org/t/p/w500", "")

    rating, _ = Rating.objects.update_or_create(
        user=user,
        tmdb_id=tmdb_id,
        defaults={
            "value": value,
            "media_type": media_type,
            "title": title,
            "poster_path": poster_path,
        }
    )

    return JsonResponse({
        "success": True,
        "rating": rating.value
    })

# Obtiene la información del contenido guardado por el usuario y carga la vista de detalles
def content_detail(request, tmdb_id, media_type):

    content = UserContent.objects.filter(
        user=request.user,
        tmdb_id=tmdb_id,
        media_type=media_type

    ).first()

    # Prepara la información que será enviada al template
    context = {
        "tmdb_id": tmdb_id,
        "media_type": media_type,
        "user_rating": content.rating if content else 0
    }

    return render(request,"details.html", context)

# Agrega o elimina un contenido de la Watchlist del usuario
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_watchlist(request):

    # Obtiene el identificador y el tipo de contenido
    tmdb_id = request.data.get("tmdb_id")
    media_type = request.data.get("media_type")

    # Ver si existe el contenido en watchlist
    item = WatchList.objects.filter(
        user=request.user,
        tmdb_id=tmdb_id,
        media_type=media_type
    ).first()

    # Si ya existe, eliminarlo
    if item:
        item.delete()

        return Response({
            "saved": False
        })

    # Filtrar la informacion del contenido y enviarla desde la interfaz
    title = request.data.get("title", "")
    poster_path = request.data.get("poster_path", "")

    # Elimina la URL base del póster para almacenar únicamente la ruta relativa
    if poster_path.startswith("https://image.tmdb.org/t/p/w500"):
        poster_path = poster_path.replace("https://image.tmdb.org/t/p/w500", "")

    # Si falta información, la consulta directamente desde la API 
    if not title or not poster_path:
        try:
            tmdb_type = "tv" if media_type == "tv" else "movie"
            res = requests.get(
                f"https://api.themoviedb.org/3/{tmdb_type}/{tmdb_id}",
                params={"api_key": settings.TMDB_API_KEY, "language": "en-US"}
            )
            tmdb_data = res.json()
            title = title or tmdb_data.get("title") or tmdb_data.get("name", "")
            poster_path = poster_path or tmdb_data.get("poster_path", "")
        except:
            pass

    WatchList.objects.create(
        user=request.user,
        tmdb_id=tmdb_id,
        media_type=media_type,
        title=title,
        poster_path=poster_path
    )

    return Response({
        "saved": True
    })

# Verifica si un contenido se encuentra guardado en la Watchlist del usuario
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_watchlist(request, tmdb_id, media_type):
    exists = WatchList.objects.filter(
        user=request.user,
        tmdb_id=tmdb_id,
        media_type=media_type
    ).exists()

    return JsonResponse({"saved": exists})


# Agrega o elimina un contenido de la lista de Favoritos del usuario autenticado
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_favorites(request):

    tmdb_id = request.data.get("tmdb_id")
    media_type = request.data.get("media_type")

    item = Favorites.objects.filter(
        user=request.user,
        tmdb_id=tmdb_id,
        media_type=media_type
    ).first()

    if item:
        item.delete()

        return Response({
            "saved": False
        })

    title = request.data.get("title", "")
    poster_path = request.data.get("poster_path", "")

    if poster_path.startswith("https://image.tmdb.org/t/p/w500"):
        poster_path = poster_path.replace("https://image.tmdb.org/t/p/w500", "")

    if not title or not poster_path:
        try:
            tmdb_type = "tv" if media_type == "tv" else "movie"
            res = requests.get(
                f"https://api.themoviedb.org/3/{tmdb_type}/{tmdb_id}",
                params={"api_key": settings.TMDB_API_KEY, "language": "en-US"}
            )
            tmdb_data = res.json()
            title = title or tmdb_data.get("title") or tmdb_data.get("name", "")
            poster_path = poster_path or tmdb_data.get("poster_path", "")
        except:
            pass

    Favorites.objects.create(
        user=request.user,
        tmdb_id=tmdb_id,
        media_type=media_type,
        title=title,
        poster_path=poster_path
    )

    return Response({
        "saved": True
    })

# Verificar si un contenido se encuentra en la lista de Favoritos del usuario
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_favorites(request, tmdb_id, media_type):
    exists = Favorites.objects.filter(
        user=request.user,
        tmdb_id=tmdb_id,
        media_type=media_type
    ).exists()

    return JsonResponse({"saved": exists})

# Actualizar automaticamente el estado de una serie segun los episodios vistos
def update_tv_status(user, tmdb_id):

    # Obtener el registro de la serie del usuario
    content = UserContent.objects.filter(
        user=user,
        tmdb_id=tmdb_id,
        media_type="tv"

    ).first()

    # Si la serie no existe, finalizar la funcion

    if not content:
        return
    
    # Contar la cantidad de episodios visto por el usuario
    watched_episodes = WatchedEpisode.objects.filter(
        user=user,
        tmdb_id=tmdb_id
    ).count()

    try:
        # Obtener el numero total de episodios desde la API
        response = requests.get(
            f"https://api.themoviedb.org/3/tv/{tmdb_id}",
            params={
                "api_key": settings.TMDB_API_KEY,
                "language": "en-US"
            }
        )

        if response.status_code != 200:
            return
        
        total_episodes = response.json().get("number_of_episodes", 0)

    except requests.exceptions.RequestException:
        return
    
    # Actualizar el estado de la serie segun el progreso del usuario
    if total_episodes > 0 and watched_episodes >= total_episodes:
        content.status = "completed"

    else:
        content.status = "watching"

    content.save()

# Cerrar sesion 
@login_required
def logout_view(request):
    logout(request)

    return redirect('home')