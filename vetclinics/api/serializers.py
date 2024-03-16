from django.utils import timezone
from datetime import datetime
from django.utils.timezone import make_aware

from rest_framework import serializers

from vetclinics.models import Appointment


class CustomDateTimeField(serializers.Field):
    """
    Кастомизированное поле сериализатора для работы с датой и временем (пока что для appointment_date).

    Позволяет изменять объекты datetime в строковый форм 'дд.мм.гггг чч:мм' и наоборот в объект datetime.
    """
    def to_representation(self, value: datetime) -> str:
        """
        Переопределение метода.
        Преобразует объект datetime в строку в формате 'дд.мм.гггг чч:мм'.

        Args:
            value (datetime): Объект datetime, который необходимо преобразовать.

        Returns:
            str: Строковое представление даты и времени в указанном формате.
        """
        return value.strftime('%d.%m.%Y %H:%M')

    def to_internal_value(self, data: str) -> datetime:
        """
        Преобразует строку в объект datetime.

        Args:
            data (str): Строка с датой и временем в формате 'дд.мм.гггг чч:мм'.

        Returns:
            datetime: Объект datetime, представляющий указанную дату и время.

        Raises:
            serializers.ValidationError: Если строка не соответствует ожидаемому формату.
        """
        try:
            return datetime.strptime(data, '%d.%m.%Y %H:%M')
        except ValueError:
            raise serializers.ValidationError("Неверный формат даты и времени. Используйте, пожалуйста,"
                                              " формат 'дд.мм.гггг чч:мм'")


class AppointmentSerializer(serializers.Serializer):
    """
    Сериализатор для модели Appointment.

    Сериализует и валидирует данные, необходимые для создания записи на прием в ветеринарную клинику.
    """
    client = serializers.IntegerField()
    appointment_date = CustomDateTimeField()
    animal_type = serializers.IntegerField()

    def validate_appointment_date(self, value: datetime) -> datetime:
        """
        Функция валидирует дату и время записи на прием.
        Также проверяет, что дата и время записи на прием не меньше текущего момента.

        Args:
            value (datetime): Дата и время записи на прием.

        Returns:
            datetime: Дата и время записи на прием, если валидация прошла успешно.

        Raises:
            serializers.ValidationError: Если дата и время записи на прием в прошедшем времени.
            serializers.ValidationError: Если формат даты и времени неверный.
        """
        try:
            appointment_date = make_aware(value)
            if appointment_date <= timezone.now():
                raise serializers.ValidationError('Нельзя записаться на прием в прошедшем времени')
            return appointment_date
        except ValueError:
            raise serializers.ValidationError('Неверный формат даты и времени')

    def create(self, validated_data: dict) -> Appointment:
        """
        Создает объект модели Appointment на основе отвалидированных входных данных.

        Args:
            validated_data (dict): Валидированные данные для создания записи на прием.

        Returns:
            Appointment: Созданный объект модели Appointment.
        """
        return Appointment.objects.create(**validated_data)
