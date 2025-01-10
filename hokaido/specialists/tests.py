from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class LoginViewTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

    def test_login_view_status_code(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_view_template(self):
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'login.html')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertRedirects(response, reverse('index'))

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Ожидаем, что мы останемся на странице входа

        # Проверка, что сообщение об ошибке есть
        self.assertContains(response, "Please enter a correct username and password.")

    def test_index_view_access(self):
        # Проверяем доступ к главной странице без аутентификации
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)  # Ожидаем редирект на страницу входа

        # Логинимся и проверяем доступ
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)