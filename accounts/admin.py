from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """ Админ-панель аккаунта """

    save_as = True
    list_display = ['username', 'is_active', 'is_staff', 'is_superuser']
    list_display_links = ['username']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'last_name', 'first_name']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': (
            'first_name', 'last_name', 'email',
        )}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
