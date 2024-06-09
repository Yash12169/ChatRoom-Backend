from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class Friendship(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]
    user1 = models.ForeignKey(User, related_name='user1_friendships', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='user2_friendships', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)




class PendingRequest(models.Model):
    token=models.TextField(default="")
    user   = models.ForeignKey(User, related_name='pending_request',on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='send_request', on_delete=models.CASCADE)
    message = models.TextField(default=" ")


class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    profile_picture = models.ImageField(blank=True,null=True,upload_to='profile_pics')
    about = models.TextField(default="hey i'm  using ChatRoom")
    friends = models.ForeignKey(Friendship, related_name='friends', on_delete=models.CASCADE,null=True)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True,null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)


class Settings(models.Model):
    settings_id = models.ForeignKey(Profile, related_name="settings", on_delete=models.CASCADE)
    Chat_background = models.CharField(max_length=255)
    theme = models.CharField(max_length=255)
    blacklisted = models.TextField(blank=True)


class BlackListedUsers(models.Model):
    user = models.ForeignKey(User, related_name="blacklisted",on_delete=models.CASCADE)
    blocked_user = models.ForeignKey(User,related_name="blacklisteduser",on_delete=models.CASCADE)


class ContactForm(models.Model):
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    message = models.TextField()
    phone = models.CharField(max_length=12,null=True)
    email = models.EmailField()