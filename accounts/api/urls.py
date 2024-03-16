from django.urls import path
from accounts.api.views import AccountRegistrationAPIView

app_name = 'accounts'

urlpatterns = [
    path('register/', AccountRegistrationAPIView.as_view(), name='account-registration'),
]
