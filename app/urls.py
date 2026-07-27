from django.urls import path 
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Página principal
    path('', views.home, name='home'),
    # Contenido por género (películas y series)
    path('genre/<int:genre_id>/', views.genre_combined, name='genre_combined'),
    # Películas por género
    path('movies/genre/<int:genre_id>/', views.movies_by_genre, name='movies_by_genre'),
    # Series por género
    path('tv/genre/<int:genre_id>/', views.tv_series_by_genre, name='tv_series_by_genre'),
    # API para obtener contenido por género
    path('api/genre/<int:genre_id>/', views.get_content_by_genre, name='get_content_by_genre'),
    # Registro de usuarios
    path('register/', views.register, name='register'),
    # Inicio de sesión
    path('login/', views.login_view, name='login'),
    # Dashboard principal del usuario
    path('dashboard/', views.dashboard, name='dashboard'),
    # Filtro de películas
    path('movies/filter/',views.filter_movies, name="filter_movies"),
    # Filtro de series
    path('tv/filter/',views.filter_tv, name="filter_tv"),
    # Filtro de anime
    path('anime/filter/',views.anime_filter, name="anime_filter"),
    # Actualización del perfil del usuario
    path('update-profile/',views.update_profile, name='update_profile'),
    # Vista de detalles del contenido
    path('details/<str:media_type>/<int:tmdb_id>/',views.details, name='details'),
    # Cierre de sesión
    path('logout/', views.logout_view, name='logout'),
    # Obtener los episodios de una temporada
    path('tv/<int:tmdb_id>/season/<int:season_number>/',views.get_season_episodes, name='get_season_episodes'),
    # Marcar o desmarcar un episodio como visto
    path('toggle_episode/', views.toggle_episode, name='toggle_episode'),
    # Marcar o desmarcar una temporada como vista
    path('toggle_season/', views.toggle_season, name='toggle_season'),
    # Marcar o desmarcar una película como vista
    path('toggle_movie/', views.toggle_movie, name='toggle_movie'),
    # Verificar si una película fue marcada como vista
    path('check_movie/<int:tmdb_id>/', views.check_movie, name="check_movie"),
    # Verificar si una temporada fue marcada como vista
    path('check_season/<int:tmdb_id>/<int:season_number>/',views.check_season, name='check_season'),
    # Verificar si un episodio fue marcado como visto
    path('check_episode/<int:tmdb_id>/<int:season_number>/<int:episode_number>/', views.check_episode, name='check_episode'),
    # Guardar la calificación del usuario
    path('save_rating/', views.save_rating, name='save_rating'),
    # Mostrar información detallada del contenido
    path('content_detail/<int:tmdb_id>/<str:media_type>/',views.content_detail,name='content_detail'),
    # Agregar o eliminar contenido de la Watchlist
    path('toggle_watchlist/', views.toggle_watchlist, name='toggle_watchlist'),
    # Verificar si el contenido está en la Watchlist
    path('check_watchlist/<int:tmdb_id>/<str:media_type>/', views.check_watchlist, name='check_watchlist'),
    # Agregar o eliminar contenido de Favoritos
    path('toggle_favorites/', views.toggle_favorites, name='toggle_favorites'),
    # Verificar si el contenido está en Favoritos
    path('check_favorites/<int:tmdb_id>/<str:media_type>/', views.check_favorites, name='check_favorites'),

]

if settings.DEBUG: 
    urlpatterns += static (
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )