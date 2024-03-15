from typing import List
from django.core.management.base import BaseCommand
from django.db import transaction

from tqdm import tqdm

from vetclinics.models import AnimalType
from accounts.factories import AccountFactory


class Command(BaseCommand):
    help: str = 'Загрузка AnimalTypes, Accounts'

    @transaction.atomic
    def handle(self, *args: List[str], **kwargs: dict) -> None:
        """
        Хелпер-загрузчик данных в модель AnimalType.

        :param args: Список аргументов командной строки (пока не используется).
        :param kwargs: Словарь именованных аргументов командной строки (пока не используется).
        """
        animal_types: List[str] = [
            'Кошка',
            'Собака',
            'Попугай',
            'Крокодил',
        ]

        total_anemal_types: int = len(animal_types)
        with tqdm(total=total_anemal_types, desc='Загрузка типов животных', unit='Тип животного') as pbar:
            for name in animal_types:
                animal_type, created = AnimalType.objects.get_or_create(name=name)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Тип животного "{name}" создан успешно.'))
                else:
                    self.stdout.write(self.style.WARNING(f'Тип животного "{name}" уже существует.'))
                pbar.update(1)
