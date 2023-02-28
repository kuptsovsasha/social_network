from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse
from django.views.generic import ListView, CreateView

from social_network.chat.models import Message
from social_network.user_profile.models import Profile, FriendList


class ChatsListView(LoginRequiredMixin, ListView):
    model = FriendList
    template_name = 'chats/chat_friends.html'
    context_object_name = 'friends'
    paginate_by = 10

    def get_queryset(self):
        """
        :return profiles which have chats with request user
        """
        # get request user profile
        profile = Profile.objects.get(user=self.request.user)
        # make list with profile ids with whom user already have conversation
        friends_chats_ids = list(Message.objects.filter(author=profile).values_list('receiver_id', flat=True))
        if friends_chats_ids:
            # if user already write to someone - add ids profile who write to user
            friends_chats_ids.extend(list(Message.objects.filter(receiver=profile).values_list('author_id', flat=True)))
        else:
            friends_chats_ids = list(Message.objects.filter(receiver=profile).values_list('author_id', flat=True))
        # get all profiles base on friends chats ids
        try:
            friends = Profile.objects.filter(id__in=friends_chats_ids).order_by('user__username')
            return friends
        except TypeError:
            print("Profile haven't messages yet!")
        return []


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'chats/chat.html'
    context_object_name = 'messages'
    paginate_by = 10

    def get_queryset(self):
        """
        :return all messages (if exist) with given friend id and  request user
        """
        profile = Profile.objects.get(user=self.request.user)
        friend = Profile.objects.get(id=self.kwargs.get('friend_id'))
        messages = Message.objects.filter(Q(author=profile, receiver=friend) |
                                          Q(author=friend, receiver=profile)).order_by('created_at')
        return messages

    def get_context_data(self, **kwargs):
        """
        Update context with request user profile and friend_id
        for have possibility create new messages
        """
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        context['profile'] = profile
        context['friend_id'] = self.kwargs.get('friend_id')
        return context


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['message']
    template_name = 'chats/chat.html'

    def form_valid(self, form):
        # create message and add to form author and receiver
        form.instance.author_id = self.request.user.profile.id
        form.instance.receiver_id = self.kwargs['receiver_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('messages', kwargs={'friend_id': self.kwargs['receiver_id']})
