from django.shortcuts import render, redirect
from .models import ExcelFile
import pandas as pd


# Create your views here.
def login_view(request):
    return render(request, "login.html")


def index(request):
    return render(request, "index.html")


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
