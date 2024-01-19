from rest_framework import serializers
from .models import Message, Friendship,PendingRequest,User,Profile,BlackListedUsers

class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id','username')
        model = User
class SendMessageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('receiver', 'content','timestamp')
        model = Message

class ReceiveMessageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('sender','receiver' ,'content')
        model = Message


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id','user','message')
        model = PendingRequest

class ListRequestSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id','user','sender','message')
        model = PendingRequest

class AcceptFriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id','user', 'message','sender')
        model = PendingRequest

class RejectFriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'user', 'sender', 'message')
        model = PendingRequest

class ListFriendsSerializer(serializers.ModelSerializer):
    friend_id = serializers.SerializerMethodField()
    class Meta:
        fields = ('friend_id','created_at')
        model = Friendship

    def get_friend_id(self, obj):
        request_user_id = self.context['request'].user.id
        if obj.user1_id == request_user_id:
            return obj.user2_id
        elif obj.user2_id == request_user_id:
            return obj.user1_id
        else:
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


class BlackListSerializer(serializers.ModelSerializer):
    class Meta:
        fields=('blocked_user',)
        model = BlackListedUsers

class ListBlackListSerializer(serializers.ModelSerializer):
    class Meta:
        fields=('blocked_user',)
        model = BlackListedUsers

class ShowSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        fields=('user','about')
        model =Profile


class ListMessageSerializer(serializers.ModelSerializer):
    class Meta:
        fields=('sender',)
        model = Message