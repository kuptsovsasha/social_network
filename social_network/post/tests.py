from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from .models import Post

User = get_user_model()


class PostCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='testuser@email.com', password='Testpass123')
        self.client.login(email='testuser@email.com', password='Testpass123')
        self.url = reverse('post_create')

    def test_post_create_view_success(self):
        data = {
            'content': 'Test post text'
        }
        response = self.client.post(self.url, data=data, follow=True)

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(Post.objects.count(), 1)

        post = Post.objects.first()
        self.assertEqual(post.content, 'Test post text')
        self.assertEqual(post.author, self.user.profile)
