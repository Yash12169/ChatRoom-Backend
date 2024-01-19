from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
urlpatterns = [

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('authentication/', include('authentication.urls')),
    path('messager/', include('messager.urls')),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh')
]