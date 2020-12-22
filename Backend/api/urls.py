from django.urls import path, include
from .views import TripView, TripSearchView, AccountView, LogoutView, RegisterView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()

router.register('register', RegisterView, basename='register')
router.register('logout', LogoutView, basename='logout')
router.register('trips', TripView, basename='trips')
router.register('account', AccountView, basename='account')
router.register('search', TripSearchView, basename='search')


urlpatterns = [
    path('', include(router.urls)),
    path('user-auth/', obtain_auth_token, name='user-auth'),
    #path('account/login', ),
    #path('flights/', api_all_user_flights_view, name='all_flights'),

]