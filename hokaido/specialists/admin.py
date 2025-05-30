from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ExcelFile, Account, Position, TypeOfDish, Checklist, PhotoGallery, Menu, ExcelDataForm, TestResult
import pandas as pd

admin.site.site_header = "Администрирование HOKAIDO"  # Заголовок панели администратора
admin.site.site_title = "Администрирование HOKAIDO"  # Заголовок на вкладке браузера
admin.site.index_title = "Администрирование HOKAIDO"  # Текст на главной странице админки


class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'middle_name',
        'position', 'phone', 'is_active', 'is_staff'
    )
    search_fields = ('username', 'phone', 'first_name', 'last_name')
    list_filter = ('position', 'is_active', 'is_staff', 'date_joined')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {
            'fields': (
                'last_name', 'first_name', 'middle_name', 'photo', 'date_of_birth', 'position', 'phone', 'email',
                'additional_info')
        }),
        ('Разрешения', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)  # Скрыть по умолчанию
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2')
        }),
    )

    readonly_fields = ('last_login', 'date_joined')  # Поля для чтения

    # Переопределяем метод сохранения для хэширования паролей
    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password') and not obj.pk:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('position')  # Оптимизация запросов

    def middle_name(self, obj):
        return obj.middle_name or 'Не указано'  # Отображение значения по умолчанию

    middle_name.short_description = 'Отчество'  # Заголовок в админке


class PositionAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    search_fields = ("title", "description")
    fields = ("title", "description")


class TypeOfDishAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")
    fields = ("name", "description")


class ChecklistAdmin(admin.ModelAdmin):
    list_display = ("position", "description")
    search_fields = ("position", "description")
    list_filter = ('position',)
    fields = ("position", "description")


class PhotoGalleryAdmin(admin.ModelAdmin):
    list_display = ("date", "photo", "description")
    search_fields = ("date", "description")
    list_filter = ('date',)
    fields = ("date", "photo", 'description')


class MenuAdmin(admin.ModelAdmin):
    list_display = ("type_of_dish", 'name', "photo", "compound")
    search_fields = ("type_of_dish", "name")
    list_filter = ('type_of_dish',)
    fields = ("type_of_dish", 'name', "photo", "compound")


class TestResultAdmin(admin.ModelAdmin):
    list_display = ("user", "test_type", "dish_type", "correct", "total", "date_completed")
    list_filter = ("test_type", "dish_type", "date_completed")
    search_fields = ("user__username", "dish_type__name")
    fields = ("user", "test_type", "dish_type", "correct", "total", "date_completed")
    readonly_fields = ("date_completed",)

class PositionTypeOfDishAdmin(admin.ModelAdmin):
    list_display = ()

class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at', 'display_excel_content')

    def display_excel_content(self, obj):
        return f'<a href="{obj.file.url}">Download</a>'

    display_excel_content.allow_tags = True
    display_excel_content.short_description = 'Download'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Получаем объект ExcelFile
        excel_file = self.get_object(request, object_id)
        if request.method == 'POST':
            form = ExcelDataForm(request.POST, excel_file=excel_file)
            if form.is_valid():
                # Здесь можно обработать данные и сохранить их
                # Например, перезапись файла с новыми данными
                pass
        else:
            form = ExcelDataForm(excel_file=excel_file)

        context = {
            'form': form,
            'excel_file': excel_file,
        }
        return super().change_view(request, object_id, form_url, extra_context=context)


admin.site.register(Account, AccountAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(TypeOfDish, TypeOfDishAdmin)
admin.site.register(Checklist, ChecklistAdmin)
admin.site.register(PhotoGallery, PhotoGalleryAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(ExcelFile, ExcelFileAdmin)
admin.site.register(TestResult, TestResultAdmin)

