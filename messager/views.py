from django.shortcuts import render
from .models import Message,Friendship,PendingRequest,User,Profile,BlackListedUsers
from .serializers import SendMessageSerializer,FriendRequestSerializer, ListMessageSerializer,ListBlackListSerializer,BlackListSerializer,ShowSearchResultSerializer,DeleteAccountSerializer,AcceptFriendRequestSerializer, ChangePasswordSerializer,RejectFriendRequestSerializer, ListProfileSerializer,RemoveFriendSerializer,ListUserSerializer, ListFriendsSerializer, ListRequestSerializer,ReceiveMessageSerializer
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django_ratelimit.decorators import ratelimit
from chatroom.consumer import send_realtime_message
class SendMessageView(APIView):
        permission_classes = (IsAuthenticated,)
        def post(self, request):
            try:
                serializer = SendMessageSerializer(data=request.data)
                if serializer.is_valid():
                    sender = request.user
                    content = serializer.validated_data['content']
                    receiver = serializer.validated_data['receiver']
                    are_friends = Friendship.objects.filter(models.Q(user1=request.user,user2=receiver) |models.Q(user1=receiver,user2=request.user)).exists()
                    if not are_friends:
                        return Response({'message':f'{request.user} is not friends with {receiver}'},status=status.HTTP_400_BAD_REQUEST)

                    Message.objects.create(
                        sender=sender,
                        receiver=receiver,
                        content=content,
                    )
                    send_realtime_message(sender, receiver, content)

                    return Response({'message':'message sent successfully','data':serializer.data},status=status.HTTP_200_OK)

                return Response({'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'message':str(e)},status=status.HTTP_400_BAD_REQUEST)

class RetrieveMessageView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        message = Message.objects.filter(receiver=request.user)
        serializer = ReceiveMessageSerializer(message,many=True)
        return Response({'messages':serializer.data}, status=status.HTTP_200_OK )

class ListMessageView(APIView):
    # permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            serializer = ListMessageSerializer(data=request.data)
            if serializer.is_valid():

                person1= request.user
                person2= serializer.validated_data['receiver']
                messages = Message.objects.filter(models.Q(sender=person1,receiver=person2)|models.Q(sender=person2,receiver=person1)).order_by('timestamp')
                print(messages)
                serializer2 = ReceiveMessageSerializer(messages,many=True)
                return Response(serializer2.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)
class SendFriendRequest(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request):
        try:
            serializer = FriendRequestSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user']
                message = serializer.validated_data['message']

                existing_friendship = Friendship.objects.filter(models.Q(user1=request.user, user2=user) | models.Q(user1=user, user2=request.user)).exists()
                if not existing_friendship:
                    PendingRequest.objects.create(
                        user=user,
                        sender=request.user,
                        message=message
                    )
                    return Response({'message': 'friend request is sent successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': f'you and {user} are already friends'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': serializer.errors},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class ListFriendRequest(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_classes = PageNumberPagination
    def get(self, request):
        blacklisted_user=BlackListedUsers.objects.filter(user=request.user)
        list = PendingRequest.objects.filter(user=request.user)
        filtered_request = list.exclude(sender__in=blacklisted_user.values_list('blocked_user',flat = True))
        serializer = ListRequestSerializer(filtered_request, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class AcceptFriendRequest(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request,request_id):
        try:
            pending_request = get_object_or_404(PendingRequest, id=request_id)
            sender = pending_request.sender
            Friendship.objects.create(
                user1=request.user,
                user2=sender
            )
            serializer = AcceptFriendRequestSerializer(pending_request)
            pending_request.delete()
            return Response({'message':f'you and {sender} are now friends','data':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':str(e)},status=status.HTTP_400_BAD_REQUEST)


class RejectFriendRequest(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request,request_id):
        try:
            pending_request = get_object_or_404(PendingRequest, id=request_id)
            serializer = RejectFriendRequestSerializer(pending_request)
            pending_request.delete()
            return Response({'message': 'you have rejected the friend request','data':serializer.data}, status=status.HTTP_200_OK)
        except Exception  as e:
            return Response({'message':str(e)},status=status.HTTP_400_BAD_REQUEST)


class ListFriends(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        friends = Friendship.objects.filter(models.Q(user1=request.user) | models.Q(user2=request.user))
        serializer = ListFriendsSerializer(friends,many=True,context={'request':request})
        return Response(serializer.data,status=status.HTTP_200_OK)


class RemoveFriend(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request,friend_id):
        try:
            remove_friend = get_object_or_404(User, id=friend_id)
            remove_friendship = Friendship.objects.get(models.Q(user1=request.user,user2=remove_friend)|models.Q(user1=remove_friend,user2=request.user))
            if remove_friendship:
                friend_username = remove_friend.username
                remove_friendship.delete()
                return Response({'message': f'you have removed {friend_username} from your friend list'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'friendship does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':str(e)},status=status.HTTP_400_BAD_REQUEST)

class ListUsers(APIView):

    def get(self, request):
            all_users = User.objects.all()
            serializer = ListUserSerializer(all_users,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)

class ListProfile(APIView):
    def get(self, request, request_id):
        # Use get_object_or_404 to retrieve the profile or return a 404 response
        profile_object = get_object_or_404(Profile, id=request_id)
        serializer = ListProfileSerializer(profile_object, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangeProfilePicture(APIView):
    pass

class ChangeAboutView(APIView):
    pass

class SetTheme(APIView):
    pass

class SetChangeBackground(APIView):
    pass

class BlackListView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request):
        try:
            serializer = BlackListSerializer(data=request.data)
            if serializer.is_valid():
                blacklist_id = serializer.validated_data['blocked_user']
                user=request.user
                already_blacklisted = BlackListedUsers.objects.filter(blocked_user=blacklist_id).exists()
                if already_blacklisted:
                    return Response({'message':'the user is already blacklisted'},status=status.HTTP_400_BAD_REQUEST)
                already_friends = Friendship.objects.filter(models.Q(user1=blacklist_id) | models.Q(user2=blacklist_id))
                friendship = already_friends.exists()
                if friendship:
                    already_friends.delete()


                BlackListedUsers.objects.create(
                    user=request.user,
                    blocked_user=blacklist_id
                )
                return Response({'message':'user blacklisted successfully'},status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':str(e)},status=status.HTTP_400_BAD_REQUEST)


class ListBlackListView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        user = request.user
        query = BlackListedUsers.objects.filter(user=user)
        serializer = ListBlackListSerializer(query,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class WhitelistView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request):
        try:
            serializer = BlackListSerializer(data=request.data)
            if serializer.is_valid():
                unblock_user_id = serializer.validated_data['blocked_user']
                blacklist_obj = BlackListedUsers.objects.filter(user=request.user,blocked_user=unblock_user_id)
                if blacklist_obj.exists():
                    blacklist_obj.delete()
                    return Response({"message": "user whitelisted successfully"},status=status.HTTP_200_OK)
                else:
                    return Response({"message": "User not found in blacklist"})
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            return Response({"message":str(e)},status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(APIView):
     permission_classes = (IsAuthenticated,)
     def post(self,request):
         try:
             serializer = ChangePasswordSerializer(data=request.data,context={'request':request})
             if serializer.is_valid():
                 user = request.user
                 current_password = serializer.validated_data['current_password']
                 new_password = serializer.validated_data['new_password']

                 #check if current password is correct
                 if not user.check_password(current_password):
                     return Response({'message':'Authentication failed current password is incorrect'})


                 user.set_password(new_password)
                 user.save()
                 return Response({'message': 'password updated successfully'}, status=status.HTTP_200_OK)

             else:
                 return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
         except Exception as e:
            return Response({'message':str(e)},status=status.HTTP_400_BAD_REQUEST)


class DeleteAccount(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request):
        try:
            serializer=DeleteAccountSerializer(data=request.data)
            if  serializer.is_valid():
                user = request.user
                password=serializer.validated_data['password']
                message=serializer.validated_data['message']
                if not user.check_password(password):
                    return Response({'message':'Authentication failed'},status=status.HTTP_403_FORBIDDEN)
                if message != 'CONFIRM':
                    return Response({'message':'ERROR'},status=status.HTTP_400_BAD_REQUEST)
                user.delete()
                return Response({'message':'Account deleted successfully'},status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':str(e)},status=status.HTTP_400_BAD_REQUEST)


class SearchUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self,request):
        query=request.query_params.get('query','')
        profile=Profile.objects.filter(user__username__icontains=query)
        serializer = ShowSearchResultSerializer(profile,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
