from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django import forms
import pandas as pd


class AccountManager(BaseUserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        if username is None:
            username = ""

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Хэширование пароля
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Убедитесь, что все обязательные поля установлены
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        if 'first_name' not in extra_fields or 'last_name' not in extra_fields:
            raise ValueError("Superuser must have first_name and last_name.")
        return self.create_user(username, email, password, **extra_fields)


class Account(AbstractUser):
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    middle_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Отчество")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    photo = models.ImageField(upload_to='accounts/photos/',blank=True, null=True, verbose_name="Фото")
    position = models.ForeignKey(
        'Position',
        on_delete=models.CASCADE,
        verbose_name="Должность",
        blank=True, null=True,
        related_name="specialists"
    )
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Почта")
    additional_info = models.TextField(blank=True, null=True, verbose_name="Дополнительная информация")

    objects = AccountManager()

    # Уникальные related_name для групп и разрешений
    groups = models.ManyToManyField(
        Group,
        related_name='account_set',  # Уникальное имя
        blank=True,
        verbose_name="Groups"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='account_set',  # Уникальное имя
        blank=True,
        verbose_name="User permissions"
    )

    class Meta:
        verbose_name = "Аккаунт"
        verbose_name_plural = "Аккаунты"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()
        return full_name


class Position(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"

    def __str__(self):
        return self.title


class TypeOfDish(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name = "Тип блюда"
        verbose_name_plural = "Типы блюд"

    def __str__(self):
        return self.name


class Checklist(models.Model):
    position = models.ForeignKey(
        'Position',  # Исправлено на 'Position'
        on_delete=models.CASCADE,
        verbose_name="Должность",
        related_name="checklists"
    )
    description = models.TextField(verbose_name="Чек-лист")

    class Meta:
        verbose_name = "Чек-лист"
        verbose_name_plural = "Чек-листы"

    def __str__(self):
        return self.position.title  # Исправлено на title, так как __str__ у Position возвращает title


class PhotoGallery(models.Model):
    date = models.DateField(verbose_name="Дата публикации")
    photo = models.ImageField(upload_to='photogallery/photos/', verbose_name="Фото")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"
        ordering = ['-date']

    def __str__(self):
        return str(self.date)  # Преобразование даты в строку для отображения


class Menu(models.Model):
    type_of_dish = models.ForeignKey(
        'TypeOfDish',
        on_delete=models.CASCADE,
        verbose_name="Тип блюда",  # Исправлено на "Тип блюда" вместо "Должность"
        related_name="menus"
    )
    name = models.CharField(max_length=200, unique=True, verbose_name="Название")
    photo = models.ImageField(upload_to='menu/photos/', blank=True, null=True, verbose_name="Фото блюда")
    compound = models.TextField(verbose_name="Состав")

    class Meta:
        verbose_name = "Меню"
        verbose_name_plural = "Меню"

    def __str__(self):
        return self.name


class ExcelFile(models.Model):
    file = models.FileField(upload_to='excel_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    def get_excel_data(self):
        # Чтение данных из Excel файла
        file_path = self.file.path
        df = pd.read_excel(file_path)
        return df


class ExcelDataForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        excel_file = kwargs.pop('excel_file', None)
        super().__init__(*args, **kwargs)

        if excel_file:
            df = excel_file.get_excel_data()
            # Преобразование данных DataFrame в строку для текстового поля
            self.fields['data'].initial = df.to_string(index=False)
