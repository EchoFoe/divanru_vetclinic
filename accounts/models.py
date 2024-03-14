from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class Account(AbstractUser):
    groups = models.ManyToManyField(Group, verbose_name='Группы', blank=True, related_name='user_accounts')
    user_permissions = models.ManyToManyField(Permission, verbose_name='Разрешения пользователя', blank=True,
                                              related_name='user_accounts')
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name='Телефон')
    telegram_chat_id = models.CharField(max_length=120, blank=True, verbose_name='ID телеграм чата')

    class Meta:
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'

    def __str__(self):
        return 'Пользователь %s %s' % (self.first_name, self.last_name)

    def get_full_name(self):
        return f'{self.first_name.capitalize()} {self.last_name.capitalize()}'
