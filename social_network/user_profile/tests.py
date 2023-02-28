from io import BytesIO

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from .models import Profile, FriendList, FriendRequest
from .serializers import ProfileSerializer
from social_network.post.models import Post

User = get_user_model()


class ProfileDetailViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='Testpass1', email="testuser@email.com"
        )
        self.profile = Profile.objects.get(user=self.user)
        self.post = Post.objects.create(
            author=self.profile, content='Test Content'
        )
        self.url = reverse('profile')

    def test_profile_detail_view(self):
        self.client.login(email='testuser@email.com', password='Testpass1')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/profile.html')
        self.assertEqual(response.context['profile'], self.profile)
        self.assertIn(self.post, response.context['posts'])

    def test_profile_detail_view_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class FriendProfileDetailViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='Testpass1', email="testuser@email.com"
        )
        self.friend = User.objects.create_user(
            username='friendtuser', password='Testpass2', email="frienduser@email.com"
        )
        self.profile = Profile.objects.get(user=self.friend)
        self.post = Post.objects.create(
            author=self.profile, content='Test Content'
        )
        self.url = reverse('friend_profile', args=[self.profile.id])

    def test_friend_profile_detail_view(self):
        self.client.login(email='testuser@email.com', password='Testpass1')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/profile.html')
        self.assertEqual(response.context['profile'], self.profile)
        self.assertIn(self.post, response.context['posts'])

    def test_friend_profile_detail_view_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_friend_profile_detail_view_with_nonexistent_profile_id(self):
        self.client.login(email='testuser@email.com', password='Testpass1')
        url = reverse('friend_profile', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ProfileUpdateViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='Testpassword1'
        )
        self.profile = Profile.objects.get(user=self.user)
        self.url = reverse('update_profile')

    def test_get_profile(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = ProfileSerializer(self.profile).data
        self.assertEqual(response.data, expected_data)

    def test_update_profile(self):
        self.client.force_login(self.user)
        image_file = BytesIO()
        Image.new('RGB', (100, 100)).save(image_file, 'jpeg')
        image_file.seek(0)
        data = {
            'profile_image': image_file,
            'gender': 'F',
        }
        response = self.client.put(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.user.gender, 'F')
        self.assertIsNotNone(self.profile.profile_image)


class ProfileFriendsListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@email.com', password='Testpass123')
        self.profile1 = Profile.objects.get(user=self.user1)
        self.friend_list1 = FriendList.objects.create(profile=self.profile1)
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@email.com', password='Testpass123')
        self.profile2 = Profile.objects.get(user=self.user2)
        self.friend_list2 = FriendList.objects.create(profile=self.profile2)

    def test_profile_friends_list_view_when_logged_in(self):
        self.client.login(email='testuser1@email.com', password='Testpass123')
        url = reverse('friends')
        response = self.client.get(url)

        # check if url correct and return right template with empty array for friends and friends_requests
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'friends/friends.html')
        self.assertQuerysetEqual(response.context['friends'], [])
        self.assertQuerysetEqual(response.context['friends_request'], [])

        # create friend request and check if response contains this request
        self.friend_request = FriendRequest.objects.create(sender=self.profile2, receiver=self.profile1)
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['friends_request'], [self.friend_request])

        # accept request from profile2  and check if response now contains friends profile and friends request empty
        self.friend_request.accept()
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['friends'], [self.profile2])
        self.assertQuerysetEqual(response.context['friends_request'], [])

    def test_profile_friends_list_view_when_not_logged_in(self):
        url = reverse('friends')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class SendFriendRequestViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='testuser1@example.com',
            password='Testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='testuser2@example.com',
            password='Testpass123'
        )
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile2 = Profile.objects.get(user=self.user2)
        self.client.login(email='testuser1@example.com', password='Testpass123')

    def test_send_friend_request(self):
        """Test that sending a friend request creates a FriendRequest object"""
        url = reverse('send_friend_request', kwargs={'friend_id': self.profile2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        friend_request = FriendRequest.objects.filter(sender=self.profile1, receiver=self.profile2)
        self.assertTrue(friend_request.exists())
