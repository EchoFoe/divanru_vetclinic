import factory
from faker import Faker

from django.contrib.auth import get_user_model

fake = Faker()
User = get_user_model()


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda _: User.objects.make_random_password(length=10))
    first_name = factory.LazyAttribute(lambda _: fake.first_name()[:20])
    last_name = factory.LazyAttribute(lambda _: fake.last_name()[:20])
    phone = factory.LazyAttribute(lambda _: fake.phone_number()[:15])
    telegram_chat_id = factory.LazyAttribute(lambda _: str(fake.random_int(min=1000000000, max=9999999999)))
