from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from messager.models import User,Profile
from django.contrib.auth.hashers import make_password
from .serializers import UserRegistrationSerializer

class HomeView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        content = {'message' : "login is successful"}
        return Response(content)


class LogOutView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)

            if 'access' in token:
                raise ValueError('wrong type of token provided')

            token.blacklist()
            return Response({'message': 'successfully logged out'}, status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response({'message' : str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(APIView):
    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                username = serializer.validated_data['username']
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                about = serializer.validated_data['about']
                # profile_picture = serializer.validated_data['profile_picture']
                hashed_password = make_password(password)
                user = User.objects.create(
                    username=username,
                    email=email,
                    password=hashed_password,
                    is_active=True
                )
                profile=Profile.objects.create(
                    user=user,
                    about=about
                    # profile_picture=profile_picture
                )
                return Response({'message': 'New user is successfully created'},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Validation failed', 'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# one use of serializer is to do json data validation from client side
# Serializer(data=request.data)
#
# second use of serializer is to convert orm object into json from server side
# Serializer(instance=object)
