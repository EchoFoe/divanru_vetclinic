from django.contrib import admin
from .forms import AppointmentForm
from .models import AnimalType, Appointment


@admin.register(AnimalType)
class AnimalTypeAdmin(admin.ModelAdmin):
    """ Админ-панель вида животного """

    save_as = True
    list_display = ['name', 'slug', 'created_at', 'updated_at', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_display_links = ['name']
    list_filter = ['is_active', 'name']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': (('name', 'slug'),)
        }),
        ('Статус вида животного', {
            'fields': ('is_active',)
        }),
        ('Даты', {
            'fields': (('created_at', 'updated_at'),)
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """ Админ-панель для записи на приём """

    save_as = True
    form = AppointmentForm
    list_display = ['client', 'appointment_date', 'animal_type', 'created_at', 'updated_at']
    list_display_links = ['client']
    date_hierarchy = 'appointment_date'
    list_filter = ['animal_type', 'is_active', ]
    search_fields = ['client__first_name', 'client__last_name', 'client__phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': (('client', 'animal_type'),)
        }),
        ('Даты', {
            'fields': ('appointment_date', ('created_at', 'updated_at'),)
        }),
        ('Статус записи', {
            'fields': ('is_active',)
        }),
    )

    class Media:
        js = ('admin/js/appointment_date_form.js',)
