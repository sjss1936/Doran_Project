from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Post, Like

User = get_user_model()

class UserModelTest(TestCase):

    def test_user_creation(self):
        user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('password123'))
        self.assertEqual(user.email, 'test@example.com')

class PostModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='testuser@example.com')
        self.client.login(username='testuser', password='password123')

    def test_post_creation(self):
        post = Post.objects.create(
            user=self.user,
            caption='This is a test post.'
        )
        self.assertEqual(post.user, self.user)
        self.assertEqual(post.caption, 'This is a test post.')

class LikeModelTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123', email='user1@example.com')
        self.user2 = User.objects.create_user(username='user2', password='password123', email='user2@example.com')
        self.post = Post.objects.create(user=self.user1, caption='A post to be liked.')

    def test_like_creation(self):
        like = Like.objects.create(user=self.user2, post=self.post)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(like.user, self.user2)
        self.assertEqual(like.post, self.post)

    def test_unique_like(self):
        Like.objects.create(user=self.user2, post=self.post)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Like.objects.create(user=self.user2, post=self.post)

class ViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_views', password='password123', email='viewstester@example.com')
        self.client.login(username='testuser_views', password='password123')

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index.html')

    def test_create_post_view(self):
        response = self.client.get(reverse('create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/create.html')

    def test_profile_view(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302) # Redirects to user_profile
        self.assertRedirects(response, reverse('user_profile', kwargs={'username': self.user.username}))