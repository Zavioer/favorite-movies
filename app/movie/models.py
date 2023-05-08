from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    title = models.CharField(max_length=255)
    year = models.CharField(max_length=4, null=True)
    genre = models.CharField(max_length=255)
    plot = models.TextField(null=True)
    poster = models.URLField(null=True)
    metascore = models.CharField(max_length=4)
    imdb_rating = models.CharField(max_length=255)
    imdb_id = models.CharField(max_length=255, unique=True)
    

class FavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
