#from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .ApiWrapper import SkyApi
from .api_key import api_key
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


from .models import Trip, TripPrice, CustomUser # Account
from .serializers import TripSerializer, TripPriceSerializer, UserSerializer

sky_api = SkyApi(api_key)


class RegisterView(viewsets.ViewSet):

    permission_classes = [AllowAny,]

    def create(self, request):

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

        #return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'id': token.user_id})
        

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
            return Response({'deleted_id': pk}, status=status.HTTP_200_OK)
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


class TripSearchView(viewsets.ViewSet):
     def list(self, request):
        #TO-DO: handle two requests for both ways
        print(request.data)
        resp = {}
        if request.data['date_in']:
            print("TWO WAY************")
            date_in = request.data.pop('date_in')
            print("Quering for Outbound")
            print(request.data)
            data = sky_api.browse_quotes(request.data)
            resp['outbound'] = data
            temp_origin = request.data['origin']
            temp_dest = request.data['destination']
            request.data['date_out'] = date_in
            request.data['origin'] = temp_dest
            request.data['destination'] = temp_origin
            print("Quering for Inbound")
            data = sky_api.browse_quotes(request.data)
            resp['inbound'] = data
        else:
            data = sky_api.browse_quotes(request.data)
            resp['outbound'] = data
            
        return Response(resp)