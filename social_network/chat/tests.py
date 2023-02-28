from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from social_network.chat.models import Message
from social_network.user_profile.models import Profile, FriendList

User = get_user_model()


class ChatsListViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@email.com', password='Testpass123')
        self.profile1 = Profile.objects.get(user=self.user1)
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@email.com', password='Testpass123')
        self.profile2 = Profile.objects.get(user=self.user2)
        self.message1 = Message.objects.create(author=self.profile1, receiver=self.profile2)
        self.message2 = Message.objects.create(author=self.profile2, receiver=self.profile1)

    def test_chats_list_view(self):
        self.client.login(email='testuser1@email.com', password='Testpass123')
        url = reverse('chats')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['friends'], [self.profile2])


class MessageListViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@email.com', password='Testpass123')
        self.profile1 = Profile.objects.get(user=self.user1)
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@email.com', password='Testpass123')
        self.profile2 = Profile.objects.get(user=self.user2)
        self.message1 = Message.objects.create(author=self.profile1, receiver=self.profile2, message='hello')
        self.message2 = Message.objects.create(author=self.profile2, receiver=self.profile1, message='hi')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/chats/messages/1/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_accessible_by_name(self):
        self.client.login(email='testuser1@email.com', password='Testpass123')
        response = self.client.get(reverse('messages', kwargs={'friend_id': self.profile2.id}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(email='testuser1@email.com', password='Testpass123')
        response = self.client.get(reverse('messages', kwargs={'friend_id': self.profile2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chats/chat.html')

    def test_view_returns_messages(self):
        self.client.login(email='testuser1@email.com', password='Testpass123')
        response = self.client.get(reverse('messages', kwargs={'friend_id': self.profile2.id}))
        messages = response.context['messages']
        self.assertEqual(messages.count(), 2)
        self.assertIn(self.message1, messages)
        self.assertIn(self.message2, messages)

    def test_view_returns_profile_and_friend_id(self):
        self.client.login(email='testuser1@email.com', password='Testpass123')
        response = self.client.get(reverse('messages', kwargs={'friend_id': self.profile2.id}))
        profile = response.context['profile']
        friend_id = response.context['friend_id']
        self.assertEqual(profile, self.profile1)
        self.assertEqual(friend_id, self.profile2.id)


class MessageCreateViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@email.com', password='Testpass123')
        self.profile1 = Profile.objects.get(user=self.user1)
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@email.com', password='Testpass123')
        self.profile2 = Profile.objects.get(user=self.user2)
        self.message_data = {
            'message': 'Hello, World!'
        }

    def test_create_message(self):
        self.client.login(email='testuser1@email.com', password='Testpass123')
        response = self.client.post(reverse('message_create', kwargs={'receiver_id': self.profile2.id}),
                                    data=self.message_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.first()
        self.assertEqual(message.message, self.message_data['message'])
        self.assertEqual(message.author_id, self.profile1.id)
        self.assertEqual(message.receiver_id, self.profile2.id)

    def test_unauthenticated_user(self):
        response = self.client.post(reverse('message_create', kwargs={'receiver_id': self.profile2.id}),
                                    data=self.message_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.count(), 0)
