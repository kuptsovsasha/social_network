from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_register_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'Mypassword1',
            'password2': 'Mypassword1',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        user = User.objects.get(username=data['username'])
        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.check_password(data['password1']))


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.username = 'testuser'
        self.email = 'testuser@email.com'
        self.password = 'mypassword'
        self.user = User.objects.create_user(self.username, email=self.email, password=self.password)

    def test_login_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

        # test invalid login
        data = {
            'email': 'testuser@email.com',
            'password': 'invalidpassword',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password')

        # test valid login
        data = {
            'email': self.email,
            'password': self.password,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        # check if user is logged in
        user = authenticate(username=self.email, password=self.password)
        self.assertTrue(user is not None)
        self.assertTrue(user.is_authenticated)


class ChangePasswordViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='Testpass1', email="testuser@email.com"
        )
        self.url = reverse('change_password')
        self.client.force_authenticate(user=self.user)

    def test_change_password(self):
        data = {
            'old_password': 'Testpass1',
            'new_password': 'Newpass123'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {"message": "Password updated successfully"}
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Newpass123'))

    def test_wrong_old_password(self):
        data = {
            'old_password': 'Testpass123',
            'new_password': 'Newpass123'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"old_password_error": ["Wrong password."]},
        )

    def test_same_old_and_new_passwords(self):
        data = {
            'old_password': 'Testpass1',
            'new_password': 'Testpass1'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"new_password": ["New password can't be same as old password"]},
        )
