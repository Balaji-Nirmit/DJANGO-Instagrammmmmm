from django.contrib import admin
from .models import Notification, Profile,Post,LikePost,FollowersCount,Comment
# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(FollowersCount)
admin.site.register(Comment)
admin.site.register(Notification)