from django.urls import path
from accounts.api.views import AccountRegistrationAPIView

urlpatterns = [
    path('register/', AccountRegistrationAPIView.as_view(), name='account-registration'),
]
