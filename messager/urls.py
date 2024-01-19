from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include
from .views import SendMessageView,RetrieveMessageView,SendFriendRequest,ListFriendRequest,SearchUserView,ListMessageView,AcceptFriendRequest,RejectFriendRequest,RemoveFriend,WhitelistView,BlackListView,ListFriends,ListBlackListView,ListUsers,ListProfile,ChangePassword,DeleteAccount
urlpatterns = [
    path('send-message/', SendMessageView.as_view(), name='send-message'),
    path('retreive-message/', RetrieveMessageView.as_view(), name='retrieve-message'),
    path('listmessage/', ListMessageView.as_view(), name='list-message'),
    path('send-request/', SendFriendRequest.as_view(), name='send-request'),
    path('requests/', ListFriendRequest.as_view(), name='list-request'),
    path('requests/accept/<int:request_id>/', AcceptFriendRequest.as_view(), name='accept-request'),
    path('requests/reject/<int:request_id>/', RejectFriendRequest.as_view(), name='reject-request'),
    path('listfriends/', ListFriends.as_view(), name='list-friends'),
    path('remove-friend/<int:friend_id>/', RemoveFriend.as_view(), name='remove-friend'),
    path('listuser/', ListUsers.as_view(), name='list_user'),
    path('change-pass/', ChangePassword.as_view(), name='change_pass'),
    path('delete-acc/', DeleteAccount.as_view(), name='delete_account'),
    path('blacklist/', BlackListView.as_view(), name='blacklist'),
    path('listblacklist/', ListBlackListView.as_view(), name='listblacklist'),
    path('whitelist/', WhitelistView.as_view(), name='whitelist'),
    path('search/', SearchUserView.as_view(), name='search_user'),


]