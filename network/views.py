from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import User, Post
import json, time

#Home view: shows all posts
def index(request):
    #Get end post indexes from 
    # (i) get request from js when reached page end, or 
    # (ii) default start from beginning
    start = int(request.GET.get('start') or 0)
    end = int(request.GET.get('end') or start+10)

    all_posts = Post.objects.all()
    all_posts = all_posts.order_by("-time").all()
    return render(request, "network/index.html",{
        'posts': all_posts,
        'view_for': 'Home'
    })

#Search view: search for other users
def search(request):
    if request.method == 'POST':
        search = str(request.POST['search']).lower()
        if search == '':
            return HttpResponseRedirect(reverse(index))
        userdb = User.objects.values_list('username',flat=True)
        potential = []
        #Found an exact match
        if search in userdb:
            print('Found a match!')
            return HttpResponseRedirect(reverse(user_profile, args=(search,)))
        
        else:
            for user in userdb:
                if len(user.split(search)) > 1:
                    potential_user = User.objects.get(username=user)
                    potential.append(potential_user)
            return render(request, 'network/search.html', {
                'potential':potential
            })

#User Profile
@csrf_exempt
def user_profile(request,username):
    #PUT Request: Follow/unfollow the profile
    if request.method == 'PUT' and request.user.is_authenticated:
        curr_username=request.user
        curr_user = User.objects.get(username=curr_username)
        data = json.loads(request.body)
        print ('data received')
        #To follow the profile
        if data.get('follow') is not None:
            profile_username = data['follow']
            profile_user = User.objects.get(username=profile_username)
            curr_user.relationship.add(profile_user)
            curr_user.save()
            print (f'followed {profile_username}!')
            return JsonResponse({"message": f"followed {profile_username} successfully."}, status=201)
        #To unfollow the profile
        if data.get('unfollow') is not None:
            profile_username = data['unfollow']
            profile_user = User.objects.get(username=profile_username)
            curr_user.relationship.remove(profile_user)
            curr_user.save()
            print (f'unfollowed {profile_username}!')
            return JsonResponse({"message": f"unfollowed {profile_username} successfully."}, status=201)

    #GET Request: View the profile
    profile_owner = User.objects.get(username=username)
    profile_posts = Post.objects.filter(author=profile_owner)
    profile_posts = profile_posts.order_by("-time").all()
    print('profile view retrieved')
    return render(request, 'network/profile.html',{
        'posts':profile_posts,
        'profile_owner': profile_owner
    })

#Following View: showing only content from people the account follows
@login_required
def following(request):
    curr_username=request.user
    curr_user = User.objects.get(username=curr_username)
    all_posts = Post.objects.all()
    all_posts = all_posts.order_by("-time").all()
    following_posts = [post for post in all_posts if post.author in curr_user.relationship.all()]
    
    return render(request, "network/index.html",{
        'posts':following_posts,
        'view_for': 'Following'
    })

#Create new post: takes json object -> extracts info -> feed into model from models.py
@csrf_exempt
@login_required
def new(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print ('new post data received')
        content = data.get('content')
        author = request.user
        new_post = Post.objects.create(author=author,content=content)

        return JsonResponse({"id_created":new_post.id, "message": "Post created successfully"},status=201)

#Deals with individual posts
@csrf_exempt
def post(request, id):
    #PUT requests: update existing post
    if request.method == 'PUT' and request.user.is_authenticated:
        curr_username=request.user
        curr_user = User.objects.get(username=curr_username)
        data = json.loads(request.body)
        post = Post.objects.get(pk=id)
        print ('updated data received')

        #(i): updates post content
        if data.get('content') is not None:
            post.content = data['content']
            print ('post content updated')
        
        #(ii): updates post like count
        if data.get('like') is not None:
            if data['like'] == True:
                post.likes += 1
                post.liked_by.add(curr_user)
                print('post liked!')
            else:
                post.likes -= 1
                post.liked_by.remove(curr_user)
                print('post unliked!')
        
        #(iii): add a reply
        if data.get('reply') is not None:
            replied_by_id = data['reply']
            reply_post = Post.objects.get(pk=replied_by_id)
            post.replies.add(reply_post)
            print('comment added!')

        post.save()
        time.sleep(1)
        return JsonResponse({"message": "post updated successfully."}, status=201)

    # Else: GET Request - Show the individual post and comments if any
    main_post = Post.objects.get(pk=id)
    comments = main_post.replies.order_by("-time").all()
    
    return render (request, "network/indiv.html", {
        'main_post':main_post,
        'comments':comments
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST['first']
        last_name = request.POST['last']
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            user.first_name=first_name
            user.last_name=last_name
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
