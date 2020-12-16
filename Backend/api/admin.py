from django.contrib import admin


# Register your models here.
from .models import Trip, TripPrice, CustomUser
project_models = [Trip, TripPrice, CustomUser]
admin.site.register(project_models)
