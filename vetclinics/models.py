from django.db import models

from .bases import DateTimeBaseModel
from accounts.models import Account


class AnimalType(DateTimeBaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название вида животного')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Уникальная строка',
                            help_text='Объявляется автоматически')

    class Meta:
        verbose_name = 'Животное'
        verbose_name_plural = 'Животные'

    def __str__(self):
        return self.name


class Appointment(DateTimeBaseModel):
    client = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='client_appointments',
                               verbose_name='Клиент')
    appointment_date = models.DateTimeField(verbose_name='Дата и время записи')
    animal_type = models.ForeignKey('vetclinics.AnimalType', on_delete=models.CASCADE,
                                    related_name='animal_type_appointments', verbose_name='Вид животного')

    class Meta:
        verbose_name = 'Запись на прием'
        verbose_name_plural = 'Записи на прием'

    def __str__(self):
        return f'Запись клиента {self.client.get_full_name()} на {self.appointment_date}'
