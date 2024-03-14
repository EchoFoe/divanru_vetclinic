from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from .serializers import AccountSerializer

ACCOUNTS = 'Аккаунты (клиенты)'


class AccountRegistrationAPIView(APIView):
    @swagger_auto_schema(
        tags=[ACCOUNTS],
        request_body=AccountSerializer,
        responses={
            status.HTTP_201_CREATED: AccountSerializer(),
            status.HTTP_400_BAD_REQUEST: 'Неверные данные были предоставлены'
        },
        operation_summary='Регистрация клиента',
    )
    def post(self, request):
        """
        POST-запрос на регистрацию нового пользователя.

        Параметры запроса включает в себя json со следующей структурой:
        - first_name (строка): Имя пользователя.
        - last_name (строка): Фамилия пользователя.
        - phone (строка): Номер телефона пользователя.
        - telegram_chat_id (строка): ID чата в Telegram.

        Пример запроса:
        -   {
                "first_name": "Имя",
                "last_name": "Фамилия",
                "phone": "+1111111111",
                "telegram_chat_id": "1111111111"
            }

        Пример ответа:
        Если пользователь успешно создан, возвращается статус 201 CREATED и данные нового пользователя:
        -   {
                "id": 1,
                "first_name": "Имя",
                "last_name": "Фамилия",
                "phone": "+1111111111",
                "telegram_chat_id": "1111111111"
            }

        Если переданы некорректные данные, возвращается статус 400 BAD REQUEST и соответствующее сообщение об ошибке.
        """
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            if not username:
                User = get_user_model()
                username = User.objects.make_random_password(length=10)
                serializer.validated_data['username'] = username
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
