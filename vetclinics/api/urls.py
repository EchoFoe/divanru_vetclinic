from django.urls import path
from .views import AppointmentAPIView, FreeSlotsAPIView

app_name = 'vetclinics'

urlpatterns = [
    path('free-slots/', FreeSlotsAPIView.as_view(), name='free-slots'),
    path('make-an-appointment/', AppointmentAPIView.as_view(), name='make-an-appointment'),
]
