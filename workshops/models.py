from django.db import models

# Create your models here.
class Workshop(models.Model):
    naam = models.CharField(max_length=64, unique=True)
    max = models.IntegerField()
    # min = models.IntegerField(default=0)

    def __str__(self):
        return self.naam

class User(models.Model):
    naam = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100, blank=True)
    deleted = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.naam

class WorkshopRating(models.Model):
    workshop = models.ForeignKey(Workshop)
    user = models.ForeignKey(User)
    rating = models.IntegerField()