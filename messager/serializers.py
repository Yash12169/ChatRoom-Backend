from rest_framework import serializers
from .models import Message, Friendship,PendingRequest,User,Profile,BlackListedUsers,ContactForm

class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id','username')
        model = User
class SendMessageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('receiver','sender', 'content','timestamp')
        model = Message

class ReceiveMessageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('sender','receiver' ,'content')
        model = Message


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user','sender','token')
        model = PendingRequest





class ListRequestSerializer(serializers.ModelSerializer):
    susername = serializers.CharField(source='sender.username', read_only=True)
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'user', 'sender', 'message', 'susername', 'profile_picture')
        model = PendingRequest

    def get_profile_picture(self, instance):
        try:
            profile = Profile.objects.get(user__username=instance.sender.username)
            return profile.profile_picture.url
        except Profile.DoesNotExist:
            return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation

class AcceptFriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id','user', 'message','sender','token')
        model = PendingRequest

class RejectFriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'user', 'sender', 'message')
        model = PendingRequest


class FriendProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('profile_picture', 'about')
# class ListFriendsSerializer(serializers.ModelSerializer):
#     friend_id = serializers.SerializerMethodField()
#     profile_picture = FriendProfileSerializer(source='get_profile',read_only=True)
#     class Meta:
#         fields = ('friend_id','created_at','profile_picture')
#         model = Friendship
#
#     def get_friend_id(self, obj):
#         request_user_id = self.context['request'].user.id
#         if obj.user1_id == request_user_id:
#             return obj.user2_id
#         elif obj.user2_id == request_user_id:
#             return obj.user1_id
#         else:
#             return None
#
#     def get_profile(self, obj):
#         friend_id = self.get_friend_id(obj)
#         if friend_id is not None:
#             try:
#                 user = User.objects.get(id=friend_id)
#                 friend_profile = Profile.objects.get(user=user)
#                 return ProfileSerializer(friend_profile.profile_picture)
#             except Profile.DoesNotExist:
#                 return None
#         return None
#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         if instance.user1 == self.context['request'].user:
#             representation['username'] = instance.user2.username
#         else:
#             representation['username'] = instance.user1.username
#         return representation

class BlackListSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('blocked_user', 'user',)
        model = BlackListedUsers


class ListFriendsSerializer(serializers.ModelSerializer):
    friend_id = serializers.SerializerMethodField()
    friend_profile = serializers.SerializerMethodField()

    class Meta:
        fields = ('friend_id', 'created_at', 'friend_profile')
        model = Friendship

    def get_friend_id(self, obj):
        request_user_id = self.context['request'].user.id
        if obj.user1_id == request_user_id:
            return obj.user2_id
        elif obj.user2_id == request_user_id:
            return obj.user1_id
        else:
            return None

    def get_friend_profile(self, obj):
        friend_id = self.get_friend_id(obj)
        if friend_id is not None:
            try:
                friend = User.objects.get(id=friend_id)
                friend_profile = friend.profile
                return {
                    'profile_picture': friend_profile.profile_picture.url if friend_profile.profile_picture else None,
                    'about': friend_profile.about
                }
            except Profile.DoesNotExist:
                return None
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.user1 == self.context['request'].user:
            representation['username'] = instance.user2.username
        else:
            representation['username'] = instance.user1.username
        return representation
class RemoveFriendSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'user1', 'user2')
        model = Friendship


class ListProfileSerializer(serializers.ModelSerializer):
    friends = serializers.SerializerMethodField()
    class Meta:
        fields = ('id','about','friends')
        model = Profile
    def get_friends(self):
        friends = ListFriendsSerializer(many=True, read_only=True, context={'request': self.context.get('request')})
        return friends

class ChangePasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    class Meta:
        model = User
        fields = ('current_password','new_password')


class DeleteAccountSerializer(serializers.ModelSerializer):
    message = serializers.CharField()
    class Meta:
        fields = ('password','message')
        model = User




class ListBlackListSerializer(serializers.ModelSerializer):
    blocked_user_profile = serializers.SerializerMethodField()

    class Meta:
        fields = ('blocked_user', 'user', 'blocked_user_profile')
        model = BlackListedUsers

    def get_blocked_user_profile(self, obj):
        try:
            profile = Profile.objects.get(user=obj.blocked_user)
            return {
                'username': obj.blocked_user.username,
                'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
                'about': profile.about
            }
        except Profile.DoesNotExist:
            return {
                'username': obj.blocked_user.username,
                'profile_picture': None,
                'about': None
            }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            profile = Profile.objects.get(user=instance.blocked_user)
            representation['blocked_user_profile'] = {
                'username': instance.blocked_user.username,
                'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
                'about': profile.about
            }
        except Profile.DoesNotExist:
            representation['blocked_user_profile'] = {
                'username': instance.blocked_user.username,
                'profile_picture': None,
                'about': None
            }
        return representation

class ShowSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        fields=('user','about','profile_picture',)
        model =Profile
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['username']= instance.user.username
        return representation



class ListMessageSerializer(serializers.ModelSerializer):
    class Meta:
        fields=('receiver',)
        model = Message

# class FriendshipStatusSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields=('status',)
#         model = FriendshipStatus



class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = ('firstname', 'lastname', 'phone', 'email', 'message')


class UsernameAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)


class EmailAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email',)


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


# class FetchProfilePictureSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ('profile_picture',)


class FetchProfilePictureSerializer(serializers.Serializer):
    profile_picture = serializers.ImageField()


class FetchAboutSerializer(serializers.Serializer):
    about = serializers.DictField()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('about','profile_picture')
class UsernameSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = User
        fields = ('username','id','profile')






class ChangeAboutSerializerProfile(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('about',)

class ChangeAboutSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()  # Change to IntegerField if user_id is an integer

    class Meta:
        model = Profile
        fields = ('user_id', 'about',)

    def validate_user_id(self, value):
        # Add validation logic if needed
        return value


class SendUserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()  #
    class Meta:
        model = User
        fields = ('user_id',)

    def validate_user_id(self, value):
        # Add validation logic if needed
        return value