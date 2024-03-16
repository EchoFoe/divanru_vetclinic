from typing import Dict, Any

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from accounts.factories import AccountFactory

from vetclinics.models import Appointment
from vetclinics.factories import AppointmentFactory, AnimalTypeFactory, generate_valid_appointment_date


class AppointmentAPIViewTests(APITestCase):
    """
    Тесты для проверки функционала API для создания записи на прием.
    """

    def setUp(self) -> None:
        """
        Установка тестовых данных с помощью фабрик.
        """
        self.api_url_make_an_appointment = reverse('vetclinics:make-an-appointment')
        self.account = AccountFactory()
        self.animal_type = AnimalTypeFactory()
        self.appointment = AppointmentFactory()

    def test_create_appointment(self) -> None:
        """
        Проверка создания записи на прием с валидными и невалидными данными.
        """
        valid_data: Dict[str, Any] = {
            'client': self.account.id,
            'appointment_date': generate_valid_appointment_date().strftime('%d.%m.%Y %H:%M'),
            'animal_type': self.animal_type.id,
        }

        invalid_data: Dict[str, Any] = {
            'client': self.account.id,
            'appointment_date': self.appointment.appointment_date.strftime('%d.%m.%Y %H:%M'),
            'animal_type': self.animal_type.id,
        }

        valid_response = self.client.post(self.api_url_make_an_appointment, valid_data, format='json')
        invalid_response = self.client.post(self.api_url_make_an_appointment, invalid_data, format='json')
        self.assertEqual(valid_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Appointment.objects.filter(id=self.appointment.id).exists())
