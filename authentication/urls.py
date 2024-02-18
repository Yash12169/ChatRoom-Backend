from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include
from .views import HomeView, LogOutView, UserRegistrationView
urlpatterns = [
          path('home/', HomeView.as_view(), name='home'),
             path('logout/', LogOutView.as_view(), name='logout'),
             path('sign-up/', UserRegistrationView.as_view(), name='sign-up'),


]