from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User=get_user_model()
# Create your models here.
class Profile(models.Model):
  user=models.ForeignKey(User,on_delete=models.CASCADE)
  # linking to the User model which is by default in django
  id_user=models.IntegerField()
  bio=models.TextField(blank=True)
  profileimg=models.ImageField(upload_to='profile_pics',default='blank-profile-picture.png')
  # this bydeafult picture will be in media folder 
  location=models.CharField(max_length=100,blank=True)

  def __str__(self):
    return self.user.username

class Post(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4)
  user = models.CharField(max_length=100)
  image = models.ImageField(upload_to='post_images')
  caption = models.TextField()
  created_at = models.DateTimeField(auto_now=True)
  # auto_now add time whenever an object is created or updated and auto_now_add add time whenever an object is created only
  no_of_likes = models.IntegerField(default=0)

  def __str__(self):
      return self.user

class LikePost(models.Model):
  post_id = models.CharField(max_length=500)
  username = models.CharField(max_length=100)

  def __str__(self):
    return self.username

class FollowersCount(models.Model):
  follower = models.CharField(max_length=100)
  user = models.CharField(max_length=100)

  def __str__(self):
      return self.user

class Comment(models.Model):
  post_id=models.CharField(max_length=100)
  username=models.CharField(max_length=100)
  comment_msg=models.CharField(max_length=1000)
  comment_time=models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.username
  # these are  inbuilt methods which are overridden and what they do is that they return a string bydeault when a object is fetched . Remember java class tutorial

class Notification(models.Model):
  NOTIFICATION_TYPES = ((1, 'Like'), (2, 'Comment'), (3, 'Follow'))

  post_id=models.CharField(max_length=100, null=True)
  sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_from_user" )
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_to_user" )
  notification_types = models.IntegerField(choices=NOTIFICATION_TYPES, null=True, blank=True)
  notification_msg = models.CharField(max_length=100, blank=True)
  date = models.DateTimeField(auto_now_add=True)
  is_seen = models.BooleanField(default=False)