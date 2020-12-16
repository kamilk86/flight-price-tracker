from __future__ import absolute_import, unicode_literals
from celery import group
from celery import task, shared_task
from .models import Trip
from .serializers import TripPriceSerializer
import random


@task(name="trip_updater")
def update_trips_prices():
    print("******** BEAT TASK TRIGGERED **************")
    #all_trips = Trip.objects.all()
    g = group(retrieve_price.s(trip.id, trip.one_way) for trip in Trip.objects.all())
    g.apply_async()


@task
def retrieve_price(trip_id, oneway):
    print(oneway)
    if oneway:
        print("---------ADDING PRICE FOR  ONEWAY TRIP: ", trip_id)
        price = random.randrange(0, 500)
        data = {
            'outbound_price': price,

        }

        serializer = TripPriceSerializer(data=data, context={'trip_id': trip_id})
        serializer.is_valid()
        serializer.save()
        print("Price added: ", price)
        return

    print("---------ADDING PRICE FOR TWOWAY!!! TRIP: ", trip_id)
    price = random.randrange(0, 500)
    price_2 = random.randrange(0, 500)
    data = {
        'outbound_price': price,
        'inbound_price': price_2

    }

    serializer = TripPriceSerializer(data=data, context={'trip_id': trip_id})
    serializer.is_valid()
    serializer.save()
    print("Prices added: ", price, " ", price_2)

    return
