from django.urls import path
from django.views.generic import TemplateView

from social_network.user_profile.views import (
    DeleteProfileView,
    FindProfilesView,
    FriendProfileDetailView,
    ProfileDetailView,
    ProfileFriendsListView,
    SendFriendRequestView,
    accept_friend_request,
    decline_friend_request,
    profile_update_view,
    remove_from_friends_list,
)

urlpatterns = [
    path("", ProfileDetailView.as_view(), name="profile"),
    path(
        "edit-profile-template/",
        TemplateView.as_view(template_name="profile/edit-profile.html"),
        name="edit_profile_template",
    ),
    path("profile/", profile_update_view, name="update_profile"),
    path("find-profiles/", FindProfilesView.as_view(), name="find_profiles"),
    path("delete_profile/", DeleteProfileView.as_view(), name="delete_profile"),
    path("friends/", ProfileFriendsListView.as_view(), name="friends"),
    path(
        "friend_profile/<int:profile_id>/",
        FriendProfileDetailView.as_view(),
        name="friend_profile",
    ),
    path(
        "send-friend-request/<int:friend_id>/",
        SendFriendRequestView.as_view(),
        name="send_friend_request",
    ),
    path(
        "remove-friend/<int:friend_id>/", remove_from_friends_list, name="remove_friend"
    ),
    path(
        "accept-friend-request/<int:friend_id>/",
        accept_friend_request,
        name="accept_friend_request",
    ),
    path(
        "decline-friend-request/<int:friend_id>/",
        decline_friend_request,
        name="decline_friend_request",
    ),
]
