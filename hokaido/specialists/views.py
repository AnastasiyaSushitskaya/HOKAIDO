from tarfile import data_filter
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ExcelFile, Account, PhotoGallery, TypeOfDish, Position, Checklist
import pandas as pd


# Create your views here.
def login_view(request):
    return render(request, "login.html")


def schedule_view(request):
    return render(request, "schedule.html")


def menu_view(request):
    types_of_dish = TypeOfDish.objects.prefetch_related('menus').all()
    return render(request, 'menu.html', {'types_of_dish': types_of_dish})


def mini_games_view(request):
    return render(request, "mini-games.html")


def specialists_view(request):
    positions = Position.objects.all()
    return render(request, 'specialists.html', {'positions': positions})


def clue_view(request):
    user_position = request.user.position
    checklists = Checklist.objects.filter(position=user_position)

    return render(request, 'clue.html', {'checklists': checklists})

def personal_view(request):
    return render(request, "personal.html")


def index(request):
    specialists = Account.objects.filter(position__isnull=False)  # Фильтруем по наличию позиции, если нужно
    # Получаем все фотографии
    photogallery = PhotoGallery.objects.all()

    # Выбираем 3 случайные фотографии
    random_photos = random.sample(list(photogallery), 3) if len(photogallery) >= 3 else photogallery
    return render(request, 'index.html', {'specialists': specialists, 'random_photos': random_photos})


def edit_excel(request, file_id):
    excel_file = ExcelFile.objects.get(id=file_id)
    df = excel_file.get_excel_data()

    if request.method == 'POST':
        # Обработка данных формы
        updated_data = request.POST.getlist('data')
        # Здесь добавьте логику для сохранения обновленных данных обратно в Excel или в БД

        # Пример: Сохранение обратно в Excel
        df.iloc[:, :] = updated_data  # Обновляем DataFrame (это нужно адаптировать)
        df.to_excel(excel_file.file.path, index=False)

        return redirect('success_url')  # Укажите ваш URL для перенаправления

    context = {
        'excel_file': excel_file,
        'data': df.values.tolist(),  # Преобразуем DataFrame в список для передачи в шаблон
    }
    return render(request, 'edit_excel.html', context)
