from datetime import timedelta

import factory

from django.utils import timezone

from accounts.factories import AccountFactory
from .models import Appointment, AnimalType


class AnimalTypeFactory(factory.django.DjangoModelFactory):
    """
    Фабрика для создания экземпляров модели AnimalType (не более 4).
    """

    class Meta:
        model = AnimalType

    name = factory.Sequence(lambda n: f'Тип животного: {n}')

    @classmethod
    def create(cls, **kwargs) -> AnimalType:
        """
        Создает и возвращает экземпляр модели AnimalType.

        Args:
            **kwargs: Дополнительные аргументы для создания объекта.

        Returns:
            AnimalType: Созданный экземпляр модели AnimalType или None, если уже создано 4 записи.
        """
        if AnimalType.objects.count() >= 4:
            return None
        return super().create(**kwargs)


class AppointmentFactory(factory.django.DjangoModelFactory):
    """
    Фабрика для создания экземпляров модели Appointment.
    """

    class Meta:
        model = Appointment

    client = factory.SubFactory(AccountFactory)
    appointment_date = factory.LazyFunction(lambda: generate_valid_appointment_date())
    animal_type = factory.SubFactory(AnimalTypeFactory)


def generate_valid_appointment_date():
    current_time = timezone.localtime()
    tomorrow = current_time + timedelta(days=1)
    start_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    end_time = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)

    valid_times = []
    time_slot = start_time
    while time_slot < end_time:
        valid_times.append(time_slot)
        time_slot += timedelta(minutes=30)

    return valid_times[-1]
