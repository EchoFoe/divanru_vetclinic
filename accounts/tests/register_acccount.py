from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response

from accounts.factories import AccountFactory
from accounts.api.serializers import AccountSerializer


class AccountRegistrationAPITest(TestCase):
    def setUp(self) -> None:
        """
        Настройка тестового клиента и url-API для регистрации аккаунта.
        """
        self.client: APIClient = APIClient()
        self.api_url: str = reverse('accounts:account-registration')

    def test_account_registration_success(self) -> None:
        """
        Тест успешной регистрации аккаунта.
        """

        account_data: dict = AccountFactory.build()
        response: Response = self.client.post(
            self.api_url,
            data={key: value for key, value in AccountSerializer(account_data).data.items() if key != 'id'}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['first_name'], account_data.first_name)
        self.assertEqual(response.data['last_name'], account_data.last_name)
        self.assertEqual(response.data['phone'], account_data.phone)
        self.assertEqual(response.data['telegram_chat_id'], account_data.telegram_chat_id)

    def test_account_registration_invalid_data(self) -> None:
        """
        Тест регистрации аккаунта с некорректными данными.
        """

        invalid_account_data: dict = {
            'first_name': 123,
            'last_name': ['User'],
            'phone': 'invalid_phone_number',
            'telegram_chat_id': 'invalid_chat_id'
        }

        response: Response = self.client.post(self.api_url, data=invalid_account_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
