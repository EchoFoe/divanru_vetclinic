from typing import List

from datetime import timedelta, datetime

from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.models import Account
from vetclinics.models import AnimalType, Appointment

from .serializers import AppointmentSerializer, AnimalTypeSerializer


VETCLINICS = 'Ветеринарная клиника'


class AppointmentAPIView(APIView):
    @swagger_auto_schema(
        tags=[VETCLINICS],
        request_body=AppointmentSerializer,
        responses={
            status.HTTP_201_CREATED: 'Запись на приём произошла успешно',
            status.HTTP_400_BAD_REQUEST: 'Неверные данные были предоставлены',
        },
        operation_summary='Запись на приём в ветклинику',
    )
    def post(self, request) -> Response:
        """
        POST-запрос для записи на прием в ветеринарную клинику.

        Параметры запроса включают в себя JSON следующей структуры:
        - client (int): ID клиента.
        - appointment_date (str): Дата и время записи на прием, например, "25.03.2024 10:00".
        - animal_type (int): ID вида животного.

        Пример запроса:
        - {
            "client": 1,
            "appointment_date": "25.03.2024 10:00",
            "animal_type": 1
          }

        Пример ответа:
        Если запись на прием прошла успешно, возвращается статус 201 CREATED.
        Если переданы некорректные данные, возвращается статус 400 BAD REQUEST и соответствующее сообщение об ошибке.
        """

        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            client_id: int = serializer.validated_data['client']
            appointment_date: str = serializer.validated_data['appointment_date']
            animal_type_id: int = serializer.validated_data['animal_type']

            client, client_error = self.get_object_or_error(Account, id=client_id)
            animal_type, animal_type_error = self.get_object_or_error(AnimalType, id=animal_type_id)

            if client_error:
                return client_error
            if animal_type_error:
                return animal_type_error

            if Appointment.objects.filter(appointment_date=appointment_date, animal_type_id=animal_type_id).exists():
                return Response('Выбранный слот уже занят', status=status.HTTP_400_BAD_REQUEST)

            serializer.save(client=client, animal_type=animal_type)
            return Response('Запись на прием произошла успешно', status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object_or_error(self, model, **kwargs):
        """
        Функция, проверяющее существование объектов в БД по заданным аргументам в сегменте моделей.
        """
        try:
            obj = model.objects.get(**kwargs)
            return obj, None
        except model.DoesNotExist:
            return None, Response(
                f'{model._meta.verbose_name} с указанным ID не существует',
                status=status.HTTP_400_BAD_REQUEST,
            )


class FreeSlotsAPIView(APIView):
    @swagger_auto_schema(
        tags=[VETCLINICS],
        operation_summary='Свободные слоты',
        responses={
            200: openapi.Response(
                description='Список свободных слотов',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                ),
            ),
            400: 'Ошибка',
        },
    )
    def get(self, request) -> Response:
        """
        Получение списка свободных слотов для записи на приём на 7 дней вперед, учитывая текущий.
        Преполагается, что часы работы клиники 09:00-18:00 без перерыва.
        Предполагается, что на каждый прием тратят 30 минут, поэтому свободные слоты с шагом 30 минут.

        Returns:
            Response: Список свободных слотов в формате ['дд.мм.гггг чч:мм'].
        """

        start_date: datetime = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date: datetime = start_date + timedelta(days=7)

        busy_slots: List[datetime] = list(Appointment.objects.filter(
            appointment_date__gte=start_date,
            appointment_date__lt=end_date
        ).values_list('appointment_date', flat=True))

        free_slots: List[datetime] = []
        current_date: datetime = start_date
        while current_date < end_date:
            if 9 <= current_date.hour < 18 and current_date not in busy_slots:
                free_slots.append(current_date)
            current_date += timedelta(minutes=30)

        formatted_free_slots: List[str] = [
            slot.strftime('%d.%m.%Y %H:%M') for slot in free_slots if slot >= timezone.localtime()
        ]

        return Response(formatted_free_slots, status=status.HTTP_200_OK)


class AnimalTypeAPIView(APIView):
    @swagger_auto_schema(
        tags=[VETCLINICS],
        operation_summary='Список типов животных',
        responses={
            200: openapi.Response(
                description='Список типов животных',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT),
                ),
            ),
            400: 'Ошибка',
        },
    )
    def get(self, request) -> Response:
        """
        Получение списка всех типов животных.

        Returns:
            Response: Список всех типов животных.
        """
        animal_types = AnimalType.objects.all()
        serializer = AnimalTypeSerializer(animal_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
