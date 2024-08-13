from django.contrib.auth import login
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required
from .models import Notification, Profile,Post,LikePost,FollowersCount,Comment
from itertools import chain
import random

# Create your views here.

@login_required(login_url="signin")
def index(request):
  user_object = User.objects.get(username=request.user.username)
  user_profile = Profile.objects.get(user=user_object)

  user_following_list = []
  feed = []

  user_following = FollowersCount.objects.filter(follower=request.user.username)

  for users in user_following:
      user_following_list.append(users.user)

  for usernames in user_following_list:
      feed_lists = Post.objects.filter(user=usernames)
      feed.append(feed_lists)

  feed_list = list(chain(*feed))

  # user suggestion starts
  all_users = User.objects.all()
  user_following_all = []

  for user in user_following:
      user_list = User.objects.get(username=user.user)
      user_following_all.append(user_list)

  new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
  current_user = User.objects.filter(username=request.user.username)
  final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
  random.shuffle(final_suggestions_list)

  username_profile = []
  username_profile_list = []

  for users in final_suggestions_list:
      username_profile.append(users.id)

  for ids in username_profile:
      profile_lists = Profile.objects.filter(id_user=ids)
      username_profile_list.append(profile_lists)

  suggestions_username_profile_list = list(chain(*username_profile_list))
  notifications=Notification.objects.filter(user=user_object)
  for i in notifications:
    profile_img=Profile.objects.get(user=User.objects.get(username=i.sender)).profileimg
    i.profileimg=profile_img
  context={
    'user_profile': user_profile, 
    'posts':feed_list, 
    'suggestions_username_profile_list': suggestions_username_profile_list[:4],
    'notifications':notifications,}
  return render(request, 'index.html', context)

def signup(request):
  if request.method=='POST':
    username=request.POST['username']
    email=request.POST['email']
    password=request.POST['password']
    password2=request.POST['password2']
    if password==password2:
      if User.objects.filter(email=email).exists():
        messages.info(request,'Email already exists')
        return redirect('signup')
      elif User.objects.filter(username=username).exists():
        messages.info(request,'Username already exists')
        return redirect("signup")
      else:
        user=User.objects.create_user(username=username,email=email,password=password)
        user.save()
        # now login the user also 
        user_login=auth.authenticate(username=username,password=password)
        auth.login(request,user_login)
        # this will create user for User table which is by default 
        # now we need to create a profile for this user in Profile table
        user_model=User.objects.get(username=username)
        new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
        new_profile.save()
        return redirect("settings")
    else:
      messages.info(request,"password not matched")
      return redirect("signup")
  else:
    return render(request,"signup.html")


def signin(request):
  if request.method=='POST':
    username=request.POST['username']
    password=request.POST['password']

    user=auth.authenticate(username=username,password=password)
    if user is not None:
      auth.login(request,user)
      return redirect('/')
    else:
      messages.info(request,"invalid credentials")
      return redirect("signin")
  else:
    return render(request, "signin.html")


@login_required(login_url="signin")
def logout(request):
  auth.logout(request)
  return redirect('signin')

@login_required(login_url="signin")
def settings(request):
  user_profile=Profile.objects.get(user=request.user)
  if request.method == 'POST':
    if request.FILES.get('image') == None:
      image = user_profile.profileimg
      bio = request.POST['bio']
      location = request.POST['location']

      user_profile.profileimg = image
      user_profile.bio = bio
      user_profile.location = location
      user_profile.save()
    elif request.FILES.get('image') != None:
      image = request.FILES.get('image')
      bio = request.POST['bio']
      location = request.POST['location']

      user_profile.profileimg = image
      user_profile.bio = bio
      user_profile.location = location
      user_profile.save()
    return redirect('settings')
  return render(request, 'setting.html', {'user_profile': user_profile})


@login_required(login_url="signin")
def upload(request):
  if request.method == 'POST':
    user = request.user.username
    image = request.FILES.get('image_upload')
    caption = request.POST['caption']

    new_post = Post.objects.create(user=user, image=image, caption=caption)
    new_post.save()

    return redirect('/')
  else:
    return redirect('/')

@login_required(login_url="signin")
def like_post(request):
  username=request.user.username
  post_id=request.GET.get('post_id')
  # this will the get the value of post_id from slug
  post=Post.objects.get(id=post_id)
  like_filter=LikePost.objects.filter(post_id=post_id,username=username).first()
  if like_filter==None:
    post.no_of_likes+=1
    post.save()
    new_like=LikePost.objects.create(post_id=post_id,username=username)
    new_like.save()
    notify=Notification.objects.create(post_id=post_id,sender=User.objects.get(username=username),user=User.objects.get(username=request.GET.get('user_id')),notification_msg="liked your post",notification_types=1)
    notify.save()
  else:
    like_filter.delete()
    post.no_of_likes-=1
    post.save()
  return redirect('/')

@login_required(login_url="signin")
def profile(request,pk):
  user_object = User.objects.get(username=pk)
  user_profile = Profile.objects.get(user=user_object)
  user_posts = Post.objects.filter(user=pk)
  user_post_length = len(user_posts)

  follower = request.user.username
  user = pk

  if FollowersCount.objects.filter(follower=follower, user=user).first():
      button_text = 'Unfollow'
  else:
      button_text = 'Follow'

  user_followers = len(FollowersCount.objects.filter(user=pk))
  user_following = len(FollowersCount.objects.filter(follower=pk))

  context = {
      'user_object': user_object,
      'user_profile': user_profile,
      'user_posts': user_posts,
      'user_post_length': user_post_length,
      'button_text': button_text,
      'user_followers': user_followers,
      'user_following': user_following,
  }
  return render(request, 'profile.html', context)

@login_required(login_url="signin")
def follow(request):
  if request.method=='POST':
    follower=request.POST['follower']
    user=request.POST['user']
    if FollowersCount.objects.filter(follower=follower,user=user).first():
      delete_follower=FollowersCount.objects.get(follower=follower,user=user)
      delete_follower.delete()
      return redirect('/profile/'+user)
    else:
      new_follower=FollowersCount.objects.create(follower=follower,user=user)
      new_follower.save()
      notify=Notification.objects.create(sender=User.objects.get(username=request.user.username),user=User.objects.get(username=user),notification_msg="started following you",notification_types=3)
      notify.save()
      return redirect('/profile/'+user)
  else:
    return redirect('/')   


@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
      username = request.POST['username']
      username_object = User.objects.filter(username__icontains=username)
# get the list of al usernames in which the username is present in the text
      username_profile = []
      username_profile_list = []

      for users in username_object:
          username_profile.append(users.id)

      for ids in username_profile:
          profile_lists = Profile.objects.filter(id_user=ids)
          username_profile_list.append(profile_lists)

      username_profile_list = list(chain(*username_profile_list))
      #  chain from the itertools module to flatten a list of lists.
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})

@login_required(login_url='signin')
def comment(request):
  if request.method=='POST':
    comment_in=request.POST['comments']
    post_id=request.POST['post_id']
    new_comment=Comment.objects.create(post_id=post_id,username=request.user.username,comment_msg=comment_in)
    new_comment.save()
    user_receive=request.POST['post_user']
    user_send=request.user.username
    user_receive=User.objects.get(username=user_receive)
    user_send=User.objects.get(username=user_send)
    notify=Notification.objects.create(post_id=post_id,sender=user_send,user=user_receive,notification_msg="commented on your post",notification_types=2)
    notify.save()
    return redirect('/')
  else:
    return redirect('/')


@login_required(login_url="signin")
def post_details(request):
  user_object=User.objects.get(username=request.user.username)
  user_profile=Profile.objects.get(user=user_object)
  post_id=request.GET.get('post_id')
  post=Post.objects.get(id=post_id)
  comment=Comment.objects.filter(post_id=post_id)
  for i in comment:
    profileimg=Profile.objects.get(user=User.objects.get(username=i.username)).profileimg
    i.profileimg=profileimg

  context = {
      'user_object': user_object,
      'user_profile': user_profile,
      'post':post,
      'comments':comment,
  }
  return render(request,'post_details.html',context)