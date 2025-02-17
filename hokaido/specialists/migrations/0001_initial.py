# Generated by Django 4.2.1 on 2025-01-10 07:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExcelFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='excel_files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PhotoGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата публикации')),
                ('photo', models.ImageField(upload_to='photogallery/photos/', verbose_name='Фото')),
            ],
            options={
                'verbose_name': 'Новость',
                'verbose_name_plural': 'Новости',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Должность',
                'verbose_name_plural': 'Должности',
            },
        ),
        migrations.CreateModel(
            name='TypeOfDish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Тип блюда',
                'verbose_name_plural': 'Типы блюд',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, unique=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='users/photos/')),
                ('last_name', models.CharField(max_length=150)),
                ('first_name', models.CharField(max_length=150)),
                ('middle_name', models.CharField(blank=True, max_length=150, null=True)),
                ('phone_number', models.CharField(max_length=20)),
                ('additional_info', models.TextField(blank=True, null=True)),
                ('password', models.CharField(max_length=128)),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specialists', to='specialists.position', verbose_name='Должность')),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название')),
                ('photo', models.ImageField(upload_to='menu/photos/', verbose_name='Фото блюда')),
                ('compound', models.TextField(verbose_name='Состав')),
                ('type_of_dish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menus', to='specialists.typeofdish', verbose_name='Тип блюда')),
            ],
        ),
        migrations.CreateModel(
            name='Checklist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(verbose_name='Чек-лист')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checklists', to='specialists.position', verbose_name='Должность')),
            ],
            options={
                'verbose_name': 'Чек-лист',
                'verbose_name_plural': 'Чек-листы',
            },
        ),
    ]
