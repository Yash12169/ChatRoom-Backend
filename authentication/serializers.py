from rest_framework import serializers
from messager.models import User
from django.contrib.auth.hashers import make_password


# class UserRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#
#     class Meta:
#         fields = ('username', 'email', 'password')
#         model = User
class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    about = serializers.CharField()

