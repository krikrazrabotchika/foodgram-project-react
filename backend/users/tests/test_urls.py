from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from users.models import User


class FollowUrlTests(APITestCase):
    """Класс для тестов url адресов подписок."""
    def setUp(self):
        self.subscriptions = 'http://testserver/api/users/subscriptions/'
        self.user_data = {
            'first_name': 'Вася',
            'last_name': 'Пупкин',
            'username': 'vasya.pupkin',
            'email': 'vpupkin@yandex.ru',
            'password': 'Qwerty_123'
        }

    def _registrate_user(self):
        """Регистрация пользователя."""
        login_url = 'http://testserver/api/users/'
        return self.client.post(
            path=login_url, data=self.user_data, format='json'
        )

    def _login_user(self):
        """Авторизация пользователя."""
        self._registrate_user()
        login_url = 'http://testserver/api/auth/token/login/'
        return self.client.post(
            path=login_url, data=self.user_data, format='json'
        )

    def _is_authenticate_user(self, mode=True):
        """Авторизация пользователя."""
        self._login_user()
        token = Token.objects.first()
        if mode:
            return self.client.credentials(
                HTTP_AUTHORIZATION='Token ' + token.key
            )
        return self.client.credentials()

    def test_not_authenticated_user_get_follow_list(self):
        """
        Тестируем недоступность url со всеми подписками
        не авторизованному пользователю.
        """
        response = self.client.get(path=self.subscriptions)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_authenticated_user_post_follow(self):
        """
        Тестируем недоступность url с подпиской на автора
        не авторизованному пользователю.
        """
        user = User.objects.create(**self.user_data)
        subscribe_url = (
            'http://testserver/api/users/'
            '{id}/subscribe/'
            .format(id=user.id)
        )
        response = self.client.get(path=subscribe_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_get_follow_list(self):
        """
        Тестируем доступность url адреса со всеми подписками
        авторизованному пользователю.
        """
        self._is_authenticate_user()
        response = self.client.get(path=self.subscriptions)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
