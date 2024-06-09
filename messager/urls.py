from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import SendMessageView,SendUser,ChangeAboutView,FetchAbout,FetchProfilePicture,RetrieveMessageView,GetCurrentUser,SaveProfilePicture,SendFriendRequest,EmailAvailability,ListFriendRequest,SearchUserView,UsernameAvailability,ListMessageView,ContactFormView,AcceptFriendRequest,RejectFriendRequest,RemoveFriend,WhitelistView,BlackListView,ListFriends,ListBlackListView,ListUsers,ListProfile,ChangePassword,DeleteAccount
urlpatterns = [
    path('send-message/', SendMessageView.as_view(), name='send-message'),
    path('retreive-message/', RetrieveMessageView.as_view(), name='retrieve-message'),
    path('listmessage/', ListMessageView.as_view(), name='list-message'),
    path('currentuser/', GetCurrentUser.as_view(), name='currentuser'),
    path('send-request/', SendFriendRequest.as_view(), name='send-request'),
    path('requests/', ListFriendRequest.as_view(), name='list-request'),
    path('requests/accept/', AcceptFriendRequest.as_view(), name='accept-request'),
    path('requests/reject/<int:request_id>/', RejectFriendRequest.as_view(), name='reject-request'),
    path('listfriends/', ListFriends.as_view(), name='list-friends'),
    path('remove-friend/', RemoveFriend.as_view(), name='remove-friend'),
    path('listuser/', ListUsers.as_view(), name='list_user'),
    path('change-pass/', ChangePassword.as_view(), name='change_pass'),
    path('delete-acc/', DeleteAccount.as_view(), name='delete_account'),
    path('blacklist/', BlackListView.as_view(), name='blacklist'),
    path('listblacklist/<int:user>/', ListBlackListView.as_view(), name='listblacklist'),
    path('whitelist/', WhitelistView.as_view(), name='whitelist'),
    path('search/', SearchUserView.as_view(), name='search_user'),
    path('contact/', ContactFormView.as_view(), name='contact_form'),
    path('availability/', UsernameAvailability.as_view(), name='username_availability'),
    path('availability-email/', EmailAvailability.as_view(), name='email_availability'),
    path('save-profile/', SaveProfilePicture.as_view(), name='save_profile_picture'),
    path('fetch-profile/<int:user_id>/', FetchProfilePicture.as_view(), name='fetch_profile_picture'),
    path('fetch-about/<int:user_id>/', FetchAbout.as_view(), name='fetch_about'),
    path('edit-about/', ChangeAboutView.as_view(), name='change_about'),
    path('send-user/', SendUser.as_view(), name='send_user'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)