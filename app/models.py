from django.db import models
from django.contrib.auth.models import User

# Crear usuario
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    about_me = models.TextField(blank=True, null=True)
    recommendations = models.BooleanField(default=False)
    newsletter = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"

# contenido activo del usuario   
class UserContent(models.Model):

    STATUS_CHOICES = [
        ("watching", "Watching"),
        ("completed", "Completed"),
        ("planned", "Plane to Watch"),
        ("dropped", "Dropped"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    tmdb_id = models.IntegerField()
    media_type = models.CharField(max_length=10)

    title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, blank=True)


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="watching"
    )

    rating = models.IntegerField(
        null=True,
        blank=True,
        default=0
    )

    watchlist =  models.BooleanField(default=False)
    favorite = models.BooleanField(default=False)


    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ["user", "tmdb_id", "media_type"]

# Registro de episodios de series que un usuario ha marcado como visto  
class WatchedEpisode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tmdb_id = models.PositiveIntegerField()
    season_number = models.IntegerField()
    episode_number = models.IntegerField()
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            "user",
            "tmdb_id",
            "season_number",
            "episode_number"
        ]


# Registro de temporadas que un usuario ha marcado como visto  
class WatchedSeason(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tmdb_id = models.IntegerField() 
    season_number = models.IntegerField()
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            "user",
            "tmdb_id",
            "season_number"
        ]

# Registro de peliculas que un usuario ha marcado como visto  
class WatchedMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tmdb_id = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            "user",
            "tmdb_id",
        ]
    

# Registro de calificacion que un usuario ha marcado con valor del 1 al 5 
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tmdb_id = models.PositiveIntegerField()
    media_type = models.CharField(max_length=10, default="movie")
    title = models.CharField(max_length=255, blank=True)
    poster_path = models.CharField(max_length=255, blank=True)
    value = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            "user",
            "tmdb_id",
        ]

    def __str__(self):
        return f"{self.user} - {self.tmdb_id} - {self.value}"
    


# Registro de lista para ver despues que un usuario ha marcado 
class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tmdb_id = models.PositiveIntegerField()
    media_type = models.CharField(max_length=10)
    title = models.CharField(max_length=255, blank=True)
    poster_path = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            "user",
            "tmdb_id",
            "media_type"
        ]

# Registro de favoritos que un usuario ha marcado en su lista
class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tmdb_id = models.PositiveIntegerField()
    media_type = models.CharField(max_length=10)
    title = models.CharField(max_length=255, blank=True)
    poster_path = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            "user",
            "tmdb_id",
            "media_type"
        ]