from django.contrib import admin

from .models import Workshop, User, WorkshopRating

class WorkshopRatingInline(admin.TabularInline):
    model = WorkshopRating

@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    pass

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [
        WorkshopRatingInline
    ]
