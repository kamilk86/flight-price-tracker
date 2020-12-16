#from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404


from .models import Trip, TripPrice, CustomUser # Account
from .serializers import TripSerializer, TripPriceSerializer, UserSerializer


class RegisterView(viewsets.ViewSet):

    permission_classes = [AllowAny,]

    def create(self, request):

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

        #return Response(status=status.HTTP_400_BAD_REQUEST)
        

class LogoutView(viewsets.ViewSet):

    def list(self, request):
        # get only the user details associated with requesting user
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class AccountView(viewsets.ViewSet):


    def list(self, request):
    
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
  

    def update(self, request, pk=None):
        # update user details
        user = CustomUser.objects.get(pk=pk)
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
        

    def destroy(self, request, pk=None):
        try:
            CustomUser.objects.get(pk=pk).delete() # request.user.id
            return Response(status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)



class TripView(viewsets.ViewSet):


    def list(self, request):
        queryset = Trip.objects.filter(owner=request.user)
        serializer = TripSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        
        serializer = TripSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

        #return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        
        queryset = Trip.objects.all()
        #q.flight_price.all()
        trip = get_object_or_404(queryset, pk=pk, owner=request.user)
        serializer = TripSerializer(trip)
        return Response(serializer.data)

    def update(self, request, pk=None):
        # Creates new trip price record related to trip
        #serializer = SingleTripPriceSerializer(data=request.data, context={'trip_id': pk})
        trip = Trip.objects.get(pk=pk)
        serializer = TripPriceSerializer(trip, data=request.data)
        serializer.is_valid()
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        try:
            Trip.objects.get(pk=pk).delete()
            return Response(status=status.HTTP_200_OK)
        except Trip.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
