from .models import Message,Friendship,PendingRequest,User,Profile,BlackListedUsers,ContactForm
from .serializers import SendMessageSerializer,EmailAvailabilitySerializer,ProfilePictureSerializer,UsernameAvailabilitySerializer,UsernameSerializer,FriendRequestSerializer,ListMessageSerializer,ContactFormSerializer,FetchProfilePictureSerializer,ListBlackListSerializer,BlackListSerializer,ShowSearchResultSerializer,DeleteAccountSerializer,AcceptFriendRequestSerializer, ChangePasswordSerializer,RejectFriendRequestSerializer, ListProfileSerializer,RemoveFriendSerializer,ListUserSerializer, ListFriendsSerializer, ListRequestSerializer,ReceiveMessageSerializer
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import models
from django.shortcuts import get_object_or_404
from chatroom.consumer import send_realtime_message

from .tasks import send_contact_email

class SendMessageView(APIView):
        permission_classes = (IsAuthenticated,)
        def post(self, request):
            try:
                serializer = SendMessageSerializer(data=request.data)
                if serializer.is_valid():
                    sender = request.user
                    content = serializer.validated_data['content']
                    receiver = serializer.validated_data['receiver']
                    are_friends = Friendship.objects.filter(models.Q(user1=request.user,user2=receiver) | models.Q(user1=receiver,user2=request.user)).exists()
                    if not are_friends:
                        return Response({'message':f'{request.user} is not friends with {receiver}'},status=status.HTTP_400_BAD_REQUEST)

                    Message.objects.create(
                        sender=sender,
                        receiver=receiver,
                        content=content,
                    )

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
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            serializer = ListMessageSerializer(data=request.data)
            if serializer.is_valid():

                person1= request.user
                person2= serializer.validated_data['receiver']
                messages = Message.objects.filter(models.Q(sender=person1,receiver=person2)|models.Q(sender=person2,receiver=person1)).order_by('timestamp')
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
                existing_friendship = Friendship.objects.filter(models.Q(user1=request.user, user2=user) | models.Q(user1=user, user2=request.user)).exists()
                if not existing_friendship:
                    PendingRequest.objects.create(
                        user=user,
                        sender=request.user,

                    )
                    return Response({'message': 'friend request is sent successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': f'you and {user} are already friends'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': serializer.errors},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class GetCurrentUser(APIView):
#     permission_classes = (IsAuthenticated,)
#     def get(self,request):
#         try:
#             username = request.user
#             user_obj=User.objects.get(username=username)
#             userprof_obj=Profile.objects.get(username=username)
#             about = userprof_obj.about
#             profile_picture = userprof_obj.profile_picture
#             serializer = UsernameSerializer(username,about,profile_picture)
#             return Response(serializer.data,status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response(str(e),status=status.HTTP_400_BAD_REQUEST)
#
class GetCurrentUser(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_obj = request.user
            serializer = UsernameSerializer(user_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

class ListFriendRequest(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):

        blacklisted_user = BlackListedUsers.objects.filter(user=request.user)
        list=PendingRequest.objects.filter(user=request.user)
        filtered_request = list.exclude(sender__in=blacklisted_user.values_list('blocked_user',flat = True))
        serializer = ListRequestSerializer(filtered_request, many=True,context={'request':request})
        return Response(serializer.data,status=status.HTTP_200_OK)


class AcceptFriendRequest(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self,request,request_id):
        try:
            pending_request = get_object_or_404(PendingRequest, id=request_id)
            sender = pending_request.sender
            Friendship.objects.create(
                user1=request.user,
                user2=sender,
                status="Accepted"
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
        serializer = ShowSearchResultSerializer(profile,many=True,context={'request':request})
        return Response(serializer.data,status=status.HTTP_200_OK)


class ContactFormView(APIView):
        def post(self,request):
            try:
                serializer = ContactFormSerializer(data=request.data)
                if serializer.is_valid():
                    firstname = serializer.validated_data['firstname']
                    lastname = serializer.validated_data['lastname']
                    phone = serializer.validated_data['phone']
                    message = serializer.validated_data['message']
                    email = serializer.validated_data['email']
                    get_form = ContactForm.objects.filter(email=email).first()
                    if get_form is not None:
                        return Response({'message':'You have recently submitted a Response wait for some time to send another'})
                    ContactForm.objects.create(
                        firstname=firstname,
                        lastname=lastname,
                        phone=phone,
                        email=email,
                        message=message
                    )
                    send_contact_email.delay(firstname,lastname,phone, email, message)
                    return Response(serializer.data,status = status.HTTP_200_OK)
                else:
                    return Response(serializer.errors,status = status.HTTP_403_FORBIDDEN)

            except Exception as e:
                return Response({'message':str(e)},status = status.HTTP_400_BAD_REQUEST)



class UsernameAvailability(APIView):
        def post(self,request):
            try:
                serializer = UsernameAvailabilitySerializer(data = request.data)
                if serializer.is_valid():
                    username = serializer.validated_data['username']
                    users = User.objects.filter(username=username)
                    if users.exists():
                        return Response({'available':False},status = status.HTTP_200_OK)
                    return Response({'available':True},status = status.HTTP_200_OK)
                else:
                    return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'message':str(e)},status = status.HTTP_400_BAD_REQUEST)



class EmailAvailability(APIView):
    def post(self,request):
        try:
            serializer = EmailAvailabilitySerializer(data = request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                users = User.objects.filter(email=email)
                if users.exists():
                    return Response({'available':False},status = status.HTTP_200_OK)
                return Response({'available':True},status = status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':str(e)},status = status.HTTP_400_BAD_REQUEST)

# class SaveProfilePicture(APIView):
#     permission_classes = (IsAuthenticated,)
#
#     def post(self, request):
#         try:
#             serializer = ProfilePictureSerializer(data=request.data)
#
#             if serializer.is_valid():
#                 profile_picture = serializer.validated_data['profile_picture']
#                 user = request.user
#                 user_prof = Profile.objects.get(user=user)
#                 user_prof.profile_picture = profile_picture
#                 user_prof.save()
#                 return Response({'message': 'Profile picture successfully updated'})
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Profile.DoesNotExist:
#             return Response({'message': 'Profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class SaveProfilePicture(APIView):
    def get(self, request, *args, **kwargs):
        # Assuming you want to get the profile picture for the current user
        profile = Profile.objects.filter(user=request.user)
        serializer = ProfilePictureSerializer(profile, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Add the user information to associate the profile picture with a user
        data = request.data.copy()
        data['user'] = request.user.id

        try:
            # Try to get the existing profile for the user
            profile = Profile.objects.get(user=request.user)
            profile_serializer = ProfilePictureSerializer(profile, data=data)
        except Profile.DoesNotExist:
            # If the profile doesn't exist, create a new one
            profile_serializer = ProfilePictureSerializer(data=data)

        if profile_serializer.is_valid():
            profile_serializer.save()
            return Response(profile_serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('error', profile_serializer.errors)
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class FetchProfilePicture(APIView):
#     # permission_classes = (IsAuthenticated, )
#     def post(self,request):
#         try:
#             serializer=FetchProfilePictureSerializer(data=request.data)
#             if serializer.is_valid():
#                 user_id = serializer.validated_data['user_id']
#                 user = User.objects.get(id=user_id)
#                 try:
#                     profile = Profile.objects.get(user=user)
#                     profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
#                     return Response(profile_picture_url,status = status.HTTP_200_OK)
#                 except Profile.DoesNotExist:
#                     return Response({'message': 'User Not found'},status = status.HTTP_404_NOT_FOUND)
#             else:
#                 return Response(serializer.errors,status= status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'message':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FetchProfilePicture(APIView):
    def get(self, request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)
            profile = get_object_or_404(Profile, user=user)
            serializer = FetchProfilePictureSerializer(profile)
            return Response(serializer.data)

        except Exception as e:
            return Response( {'message':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
