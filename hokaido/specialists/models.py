from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django import forms
import pandas as pd
import html



class AccountManager(BaseUserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        if username is None:
            username = ""

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

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
    photo = models.ImageField(upload_to='accounts/photos/', blank=True, null=True, verbose_name="Фото")
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

    groups = models.ManyToManyField(
        Group,
        related_name='account_set',
        blank=True,
        verbose_name="Groups"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='account_set',
        blank=True,
        verbose_name="User permissions"
    )

    class Meta:
        verbose_name = "Аккаунт"
        verbose_name_plural = "Аккаунты"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username}'


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
        'Position',
        on_delete=models.CASCADE,
        verbose_name="Должность",
        related_name="checklists"
    )
    description = models.TextField(verbose_name="Чек-лист")

    class Meta:
        verbose_name = "Чек-лист"
        verbose_name_plural = "Чек-листы"

    def __str__(self):
        return self.position.title


class PhotoGallery(models.Model):
    date = models.DateField(verbose_name="Дата публикации")
    photo = models.ImageField(upload_to='photogallery/photos/', verbose_name="Фото")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"
        ordering = ['-date']

    def __str__(self):
        return str(self.date)


class Menu(models.Model):
    type_of_dish = models.ForeignKey(
        'TypeOfDish',
        on_delete=models.CASCADE,
        verbose_name="Тип блюда",
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


class TestResult(models.Model):
    user = models.ForeignKey(
        'Account',
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    test_type = models.CharField(
        max_length=50,
        verbose_name="Вид теста"
    )
    dish_type = models.ForeignKey(
        'TypeOfDish',
        on_delete=models.CASCADE,
        verbose_name="Тип блюда"
    )
    correct = models.IntegerField(
        verbose_name="Правильные ответы"
    )
    total = models.IntegerField(
        verbose_name="Всего вопросов"
    )
    date_completed = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата прохождения"
    )

    class Meta:
        verbose_name = "Результат теста"
        verbose_name_plural = "Результаты тестов"
        ordering = ['-date_completed']

    def __str__(self):
        return f"{self.user}: {self.test_type} ({self.dish_type}) {self.correct}/{self.total}"


class PositionTypeOfDish(models.Model):
    position = models.ForeignKey(
        'Position',
        on_delete=models.CASCADE,
        verbose_name="Должность",
        related_name="position_dish_types"
    )
    dish_type = models.ForeignKey(
        'TypeOfDish',
        on_delete=models.CASCADE,
        verbose_name="Виды блюд, которые должен готовить"
    )

    class Meta:
        verbose_name = "Связь должностей и блюд"
        verbose_name_plural = "Связи должностей и блюд"

    def __str__(self):
        return f"{self.position}: {self.dish_type}"


class Comment(models.Model):
    user = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="comments"
    )
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']

    def __str__(self):
        return f"Комментарий от {self.user.username} ({self.created_at.date()})"


class ExcelFile(models.Model):
    file = models.FileField(upload_to='excel_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    def get_excel_data(self):
        file_path = self.file.path
        df = pd.read_excel(file_path)
        return df

    def get_html_table(self):
        df = self.get_excel_data()

        df = df.fillna('')

        html_table = '<table class="excel-table">'

        for i in range(len(df)):
            html_table += '<tr>'
            for j in range(len(df.columns)):
                cell_value = df.iloc[i, j]
                cell_value = html.escape(str(cell_value))

                cell_style = ''
                if i < 2:
                    cell_style = 'font-weight: bold; background-color: #f2f2f2;'

                html_table += f'<td style="{cell_style}">{cell_value}</td>'
            html_table += '</tr>'

        html_table += '</table>'
        return html_table


class ExcelDataForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        excel_file = kwargs.pop('excel_file', None)
        super().__init__(*args, **kwargs)

        if excel_file:
            df = excel_file.get_excel_data()

            self.fields['data'].initial = df.to_string(index=False)
