from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from social_network.post.models import Post
from social_network.user_profile.models import Profile


def home(request):
    if not request.user or not request.user.is_authenticated:
        return redirect(reverse_lazy('login'))

    profile = Profile.objects.filter(user=request.user).last()
    try:
        posts = Post.objects.filter(author__in=profile.friend_list_profile.friends.all())
        return render(request, 'index.html', {'posts': posts})
    except Exception as error:
        print(error)
        return render(request, 'index.html', {'posts': []})
