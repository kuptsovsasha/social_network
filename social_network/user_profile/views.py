from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, RedirectView, TemplateView, View
from rest_framework.decorators import api_view
from rest_framework.response import Response

from social_network.post.models import Post
from social_network.user_profile.models import FriendList, FriendRequest, Profile
from social_network.user_profile.serializers import ProfileSerializer


# -------------------------------------Profile Views-------------------------------------------------------------
class FindProfilesView(LoginRequiredMixin, TemplateView):
    template_name = "search_results_partial.html"

    def get(self, request, *args, **kwargs):
        searched_chars = self.request.GET.get("search_query")

        # Filtered profiles by username, first_name, last_name with given chars
        profiles = Profile.objects.filter(
            Q(user__username__icontains=searched_chars)
            | Q(user__first_name__icontains=searched_chars)
            | Q(user__last_name__icontains=searched_chars)
        ).exclude(user=request.user)

        requested_user_profile = Profile.objects.filter(user=request.user).last()

        # made list with request user's friends and friends requests and
        # pass them to template for have possibility show add_friend button
        friends = requested_user_profile.friends.all().values_list(
            "profile__user__email", flat=True
        )
        friends_request = FriendRequest.objects.filter(
            sender=requested_user_profile, is_active=True
        ).values_list("receiver__user__email", flat=True)

        html_results = render_to_string(
            "search_results_partial.html",
            {
                "results": profiles,
                "friends": friends,
                "friends_requests": friends_request,
            },
        )
        return JsonResponse({"html_results": html_results})


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "profile/profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # update context with request user's posts
        context["posts"] = Post.objects.filter(author=context["profile"])
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)


class FriendProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "profile/profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = Post.objects.filter(author=context["profile"])
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, id=self.kwargs["profile_id"])


@login_required
@api_view(["GET", "PUT"])
def profile_update_view(request):
    """
    get: return serialized data from user profile to edit profile form
    put: serialize and update user and user profile data
    """
    user = request.user
    profile = user.profile

    if request.method == "GET":
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


class DeleteProfileView(LoginRequiredMixin, View):
    success_url = reverse_lazy("login")

    def post(self, request, *args, **kwargs):
        # Get the user and profile objects
        user = request.user
        profile = user.profile

        # Delete the profile and user objects
        profile.delete()
        user.delete()

        # Logout the user
        logout(request)

        # Redirect to the success URL
        return redirect(self.success_url)


# ----------------------------------------------Friends Views-----------------------------------------------------
class ProfileFriendsListView(LoginRequiredMixin, ListView):
    model = FriendList
    template_name = "friends/friends.html"
    context_object_name = "friends"
    paginate_by = 10

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        try:
            return profile.friend_list_profile.friends.exclude(
                user=self.request.user
            ).order_by("user__username")
        except Exception as error:
            print(error)
            return []

    def get_context_data(self, **kwargs):
        """
        Add friends request to template context
        """
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        friends_request = FriendRequest.objects.filter(receiver=profile, is_active=True)
        context["friends_request"] = friends_request
        return context


class SendFriendRequestView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        """create Friend request and redirect to home page"""
        profile = Profile.objects.get(user=self.request.user)
        friend = get_object_or_404(Profile, id=kwargs["friend_id"])
        FriendRequest.objects.get_or_create(sender=profile, receiver=friend)
        return reverse("home")


@login_required
def remove_from_friends_list(request, friend_id):
    profile = Profile.objects.get(user=request.user)
    friend = get_object_or_404(Profile, id=friend_id)
    profile.friend_list_profile.remove_friend(friend)
    return redirect("friends")


@login_required
def accept_friend_request(request, friend_id):
    friend = get_object_or_404(
        FriendRequest, sender_id=friend_id, receiver=request.user.profile
    )
    friend.accept()
    return redirect("friends")


@login_required
def decline_friend_request(request, friend_id):
    friend = get_object_or_404(FriendRequest, sender_id=friend_id)
    friend.decline()
    return redirect("friends")
