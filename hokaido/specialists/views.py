import random
from django.shortcuts import render, redirect, get_object_or_404
from .models import ExcelFile, Account, PhotoGallery, TypeOfDish, Position, Checklist, Menu, TestResult
from django.contrib.auth.decorators import login_required


# Create your views here.
def login_view(request):
    return render(request, "login.html")


def schedule_view(request):
    return render(request, "schedule.html")


def menu_view(request):
    types_of_dish = TypeOfDish.objects.prefetch_related('menus').all()
    return render(request, 'menu.html', {'types_of_dish': types_of_dish})


def mini_games_view(request):
    context = {
        'dish_types': TypeOfDish.objects.all()  # Получаем все типы блюд из БД
    }
    return render(request, 'mini-games.html', context)


@login_required
def guess_dish_test(request, dish_type_id):
    dish_type = get_object_or_404(TypeOfDish, id=dish_type_id)

    # Получаем или создаем сессию теста
    if 'test_data' not in request.session:
        request.session['test_data'] = {
            'dish_ids': list(Menu.objects.filter(type_of_dish=dish_type).values_list('id', flat=True)),
            'current_index': 0,
            'correct': 0,
            'test_type': 'guess_dish',
            'dish_type_id': dish_type_id
        }

    test_data = request.session['test_data']

    # Если тест завершен
    if test_data['current_index'] >= len(test_data['dish_ids']):
        # Сохраняем результат
        result = TestResult.objects.create(
            user=request.user,
            test_type=test_data['test_type'],
            dish_type_id=test_data['dish_type_id'],
            correct=test_data['correct'],
            total=len(test_data['dish_ids'])
        )
        del request.session['test_data']  # Очищаем сессию
        return redirect('test_results', result_id=result.id)

    # Получаем текущее блюдо
    current_dish = Menu.objects.get(id=test_data['dish_ids'][test_data['current_index']])

    # Формируем варианты ответов
    dishes = list(Menu.objects.filter(type_of_dish=dish_type).exclude(id=current_dish.id))
    options = random.sample(dishes, min(3, len(dishes))) + [current_dish]
    random.shuffle(options)

    context = {
        'dish_type': dish_type,
        'target_dish': current_dish,
        'options': options,
        'current_progress': f"{test_data['current_index'] + 1}/{len(test_data['dish_ids'])}",
        'correct_answer': current_dish.id
    }
    return render(request, 'tests/guess_dish.html', context)


@login_required
def process_answer(request, dish_type_id):
    if request.method == 'POST' and 'test_data' in request.session:
        test_data = request.session['test_data']
        user_answer = int(request.POST.get('answer', 0))
        correct_answer = int(request.POST.get('correct_answer', 0))
        confirmed = request.POST.get('confirmed', 'false') == 'true'  # Новый параметр

        # Только при подтверждении кнопкой "Далее" считаем ответ
        if confirmed and user_answer == correct_answer:
            test_data['correct'] += 1

        # Всегда увеличиваем индекс при нажатии "Далее"
        if confirmed:
            test_data['current_index'] += 1
            request.session.modified = True

        return redirect('guess_dish_test', dish_type_id=dish_type_id)
    return redirect('mini_games')


@login_required
def test_results(request, result_id):
    result = get_object_or_404(TestResult, id=result_id, user=request.user)
    return render(request, 'tests/results.html', {'result': result})


def missing_ingredient_test(request, dish_type_id):
    dish_type = TypeOfDish.objects.get(id=dish_type_id)
    return render(request, 'tests/missing_ingredient.html', {'dish_type': dish_type})


def dish_composition_test(request, dish_type_id):
    dish_type = TypeOfDish.objects.get(id=dish_type_id)
    return render(request, 'tests/dish_composition.html', {'dish_type': dish_type})


def specialists_view(request):
    positions = Position.objects.all()
    return render(request, 'specialists.html', {'positions': positions})


def clue_view(request):
    user_position = request.user.position
    checklists = Checklist.objects.filter(position=user_position)

    return render(request, 'clue.html', {'checklists': checklists})


def personal_view(request):
    return render(request, "personal.html")


@login_required
def test_history(request):
    results = TestResult.objects.filter(user=request.user).order_by('-date_completed')
    return render(request, 'tests/history.html', {'results': results})


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
