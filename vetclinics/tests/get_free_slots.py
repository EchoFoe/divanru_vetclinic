from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.response import Response

from vetclinics.factories import AppointmentFactory


class FreeSlotsAPIViewTests(APITestCase):
    """
    Тесты для проверки функционала API для получения свободных слотов на прием.
    """

    def setUp(self) -> None:
        """
        Уставнока эндпойнта для тестов.
        """
        self.api_url_free_slots: str = reverse('vetclinics:free-slots')

    def test_get_free_slots(self) -> None:
        """
        Проверяет получение свободных слотов на прием.
        """

        AppointmentFactory.create_batch(5)
        response: Response = self.client.get(self.api_url_free_slots)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
