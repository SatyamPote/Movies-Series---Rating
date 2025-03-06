from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=200)
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True) # To prevent duplicates
    omdb_id = models.CharField(max_length=20, null=True, blank=True)
    genre = models.CharField(max_length=100, blank=True, null=True)  # Example: "Action, Sci-Fi"
    language = models.CharField(max_length=50, blank=True, null=True)
    rating = models.FloatField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    overview = models.TextField(blank=True, null=True)
    trailer_id = models.CharField(max_length=50, blank=True, null=True)  # Store YouTube video ID
    comment_count = models.IntegerField(null=True, blank=True)
    like_count = models.IntegerField(null=True, blank=True)
    upload_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

class WebSeries(models.Model):
    title = models.CharField(max_length=200)
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    omdb_id = models.CharField(max_length=20, null=True, blank=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    rating = models.FloatField(null=True, blank=True)
    first_air_date = models.DateField(null=True, blank=True)
    overview = models.TextField(blank=True, null=True)
    trailer_id = models.CharField(max_length=50, blank=True, null=True)  # Store YouTube video ID
    comment_count = models.IntegerField(null=True, blank=True)
    like_count = models.IntegerField(null=True, blank=True)
    upload_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title