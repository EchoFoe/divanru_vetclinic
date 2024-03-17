from django.urls import path
from .views import AppointmentAPIView, FreeSlotsAPIView, AnimalTypeAPIView

app_name = 'vetclinics'

urlpatterns = [
    path('animal-types/', AnimalTypeAPIView.as_view(), name='animal-types'),
    path('free-slots/', FreeSlotsAPIView.as_view(), name='free-slots'),
    path('make-an-appointment/', AppointmentAPIView.as_view(), name='make-an-appointment'),
]
