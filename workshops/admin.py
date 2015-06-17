from django.contrib import admin

from models import Workshop, User, WorkshopRating

for model in [Workshop, User, WorkshopRating]:
    admin.site.register(model, admin.ModelAdmin)
