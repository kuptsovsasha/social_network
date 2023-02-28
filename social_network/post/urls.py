from django.urls import path

from social_network.post.views import PostCreateView

urlpatterns = [
    path('create', PostCreateView.as_view(), name='post_create'),
]
