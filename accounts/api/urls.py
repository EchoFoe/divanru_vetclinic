from django.urls import path
from accounts.api.views import AccountRegistrationAPIView, UserAPIView

app_name = 'accounts'

urlpatterns = [
    path('users/<int:user_id>/', UserAPIView.as_view(), name='user-detail'),
    path('register/', AccountRegistrationAPIView.as_view(), name='account-registration'),
]
