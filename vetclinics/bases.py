from django.db import models
from django.utils import timezone


class DateTimeBaseModel(models.Model):
    """ Базовая модель с датой и временем """

    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='Дата редактирования')
    is_active = models.BooleanField(default=True, verbose_name='Активность')

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
