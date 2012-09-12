from django.db import models

# Create your models here.
class Workshop(models.Model):
	naam = models.CharField(max_length=64, unique=True)
	max = models.IntegerField()

class User(models.Model):
	naam = models.CharField(max_length=100)
	email = models.CharField(max_length=100)
	deleted = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)

class WorkshopRating(models.Model):
	workshop = models.ForeignKey(Workshop)
	user = models.ForeignKey(User)
	rating = models.IntegerField()
