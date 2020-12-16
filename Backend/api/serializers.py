from rest_framework import serializers
from .models import Trip, TripPrice, CustomUser


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password']

    def create(self, validated_data):
        user = CustomUser()
        password = validated_data.get('password')
        user.email = validated_data.get('email')
        user.set_password(password)
        user.save()

        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        password = validated_data.get('password', instance.password)
        instance.set_password(password)
        instance.save()

        return instance


class SingleTripPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = TripPrice
        fields = ['outbound_price', 'inbound_price', 'datetime_checked']

    def create(self, validated_data):
        trip_id = self.context['trip_id']
        trip = Trip.objects.get(trip_id)

        return TripPrice.objects.create(trip=trip, **validated_data)
        


class TripPriceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TripPrice
        fields = ['outbound_price', 'inbound_price', 'datetime_checked']

    def create(self, validated_data):
        
        trip_id = self.context.get("trip_id")
        trip = Trip.objects.get(pk=trip_id)

        return TripPrice.objects.create(trip=trip, **validated_data)
        # flight_id=validated_data['flight_id'], datetime_checked=validated_data['datetime_checked'], price=validated_data['price']

    def update(self, instance, validated_data):
        
        new_price = TripPrice.objects.create(trip=instance, **validated_data)

        return new_price



class TripSerializer(serializers.ModelSerializer):

    trip_price = TripPriceSerializer(many=True)

    class Meta:
        #many = True
        model = Trip
        fields = ['id', 'airline', 'one_way', 'outbound_date', 'inbound_date', 'source_city', 'destination_city', 'trip_price']

    def create(self, validated_data):
    
        user = self.context['request'].user
        trip_price = validated_data.pop('trip_price')[0]
        trip = Trip.objects.create(owner=user, **validated_data)
        TripPrice.objects.create(trip=trip, **trip_price)

        return trip

    