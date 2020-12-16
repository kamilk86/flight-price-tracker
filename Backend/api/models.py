from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email}"

class Trip(models.Model):
    owner = models.ForeignKey(get_user_model(),related_name='flight', on_delete=models.CASCADE) # ,
    created = models.DateTimeField(auto_now_add=True)
    airline = models.CharField(max_length=100)
    one_way = models.BooleanField(default=False)
    outbound_date = models.DateField()
    inbound_date = models.DateField(null=True, blank=True)
    source_city = models.CharField(max_length=100)
    destination_city = models.CharField(max_length=100)

    def __str__(self):
        return f"Trip ID: {self.id} Owner: {self.owner} airline: {self.airline} out date: {self.outbound_date} src city: {self.source_city}"


class TripPrice(models.Model):
    trip = models.ForeignKey(Trip, related_name='trip_price', on_delete=models.CASCADE)
    datetime_checked = models.DateTimeField(auto_now_add=True)
    outbound_price = models.FloatField()
    inbound_price = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.trip}"