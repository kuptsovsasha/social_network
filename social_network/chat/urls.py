from django.urls import path

from social_network.chat.views import ChatsListView, MessageCreateView, MessageListView

urlpatterns = [
    path("", ChatsListView.as_view(), name="chats"),
    path("messages/<int:friend_id>/", MessageListView.as_view(), name="messages"),
    path(
        "message/create/<int:receiver_id>/",
        MessageCreateView.as_view(),
        name="message_create",
    ),
]
