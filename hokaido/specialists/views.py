import random
from random import sample, shuffle
from django.shortcuts import render, redirect, get_object_or_404
import json
from .forms import CommentForm
from .models import ExcelFile, Account, PhotoGallery, TypeOfDish, Position, Checklist, Menu, TestResult, \
    PositionTypeOfDish, Comment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy


# Create your views here.
def login_view(request):
    return render(request, "login.html")


def schedule_view(request):
    return render(request, "schedule.html")


def menu_view(request):
    types_of_dish = TypeOfDish.objects.prefetch_related('menus').all()
    return render(request, 'menu.html', {'types_of_dish': types_of_dish})


@login_required
def mini_games_view(request):
    # Получаем все типы блюд
    all_dish_types = TypeOfDish.objects.all()

    # Для администратора показываем все тесты
    if request.user.is_superuser:
        dish_types = all_dish_types
    else:
        # Получаем должность пользователя
        user_position = request.user.position

        # Получаем типы блюд, доступные для должности пользователя
        available_dish_types = PositionTypeOfDish.objects.filter(
            position=user_position
        ).values_list('dish_type', flat=True)

        # Фильтруем типы блюд
        dish_types = all_dish_types.filter(id__in=available_dish_types)

    context = {
        'dish_types': dish_types,
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
            # 'test_type': 'guess_dish',
            'test_type': 'Угадай блюдо',
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
    try:
        result = TestResult.objects.get(id=result_id, user=request.user)
        return render(request, 'tests/results.html', {'result': result})
    except TestResult.DoesNotExist:
        return redirect('mini_games')  # Или другая страница-заглушка


@login_required
def missing_ingredient_test(request, dish_type_id):
    dish_type = get_object_or_404(TypeOfDish, id=dish_type_id)

    # Инициализация или получение данных сессии
    if 'missing_ingredient_test' not in request.session:
        request.session['missing_ingredient_test'] = {
            'dish_ids': list(Menu.objects.filter(type_of_dish=dish_type).values_list('id', flat=True)),
            'current_index': 0,
            'correct': 0,
            'test_type': 'Недостающий ингредиент',
            'dish_type_id': dish_type_id
        }

    test_data = request.session['missing_ingredient_test']

    # Проверка завершения теста
    if test_data['current_index'] >= len(test_data['dish_ids']):
        result = TestResult.objects.create(
            user=request.user,
            test_type=test_data['test_type'],
            dish_type_id=test_data['dish_type_id'],
            correct=test_data['correct'],
            total=len(test_data['dish_ids'])
        )
        # Сохраняем result_id в сессии перед удалением
        request.session['test_result_id'] = result.id
        del request.session['missing_ingredient_test']
        request.session.modified = True
        return redirect('test_results', result_id=result.id)  # Четкий редирект

    # Получение текущего блюда
    current_dish = Menu.objects.get(id=test_data['dish_ids'][test_data['current_index']])

    # Обработка состава блюда
    ingredients = [ing.strip() for ing in current_dish.compound.split(',') if ing.strip()]

    if not ingredients:
        # Если нет ингредиентов, пропускаем это блюдо
        test_data['current_index'] += 1
        request.session.modified = True
        return redirect('missing_ingredient_test', dish_type_id=dish_type_id)

    # Выбор ингредиента, который будем скрывать
    hidden_ingredient = random.choice(ingredients)

    # Создание строки с пропущенным ингредиентом
    hidden_index = ingredients.index(hidden_ingredient)
    display_ingredients = ingredients.copy()
    display_ingredients[hidden_index] = '...'
    display_compound = ', '.join(display_ingredients)

    # Подготовка вариантов ответов
    correct_answer = hidden_ingredient
    other_ingredients = []

    # Собираем ингредиенты из других блюд
    other_dishes = Menu.objects.filter(type_of_dish=dish_type).exclude(id=current_dish.id)
    for dish in other_dishes:
        if dish.compound:
            other_ingredients.extend([ing.strip() for ing in dish.compound.split(',') if ing.strip()])

    # Удаляем дубликаты и правильный ответ
    other_ingredients = list(set(other_ingredients))
    if correct_answer in other_ingredients:
        other_ingredients.remove(correct_answer)

    # Выбираем 3 случайных неправильных варианта
    wrong_answers = random.sample(other_ingredients, min(3, len(other_ingredients)))
    options = wrong_answers + [correct_answer]
    random.shuffle(options)

    context = {
        'dish_type': dish_type,
        'target_dish': current_dish,
        'display_compound': display_compound,
        'options': options,
        'correct_answer': correct_answer,
        'current_progress': f"{test_data['current_index'] + 1}/{len(test_data['dish_ids'])}"
    }

    return render(request, 'tests/missing_ingredient.html', context)


@login_required
def process_missing_ingredient(request, dish_type_id):
    if request.method == 'POST' and 'missing_ingredient_test' in request.session:
        test_data = request.session['missing_ingredient_test']
        user_answer = request.POST.get('answer', '').strip()
        correct_answer = request.POST.get('correct_answer', '').strip()

        if user_answer == correct_answer:
            test_data['correct'] += 1

        test_data['current_index'] += 1
        request.session.modified = True

        return redirect('missing_ingredient_test', dish_type_id=dish_type_id)
    return redirect('mini_games')


@login_required
def dish_composition_test(request, dish_type_id):
    dish_type = get_object_or_404(TypeOfDish, id=dish_type_id)

    # Инициализация или получение данных сессии
    if 'dish_composition_test' not in request.session:
        request.session['dish_composition_test'] = {
            'dish_ids': list(Menu.objects.filter(type_of_dish=dish_type).values_list('id', flat=True)),
            'current_index': 0,
            'correct': 0,
            'test_type': 'Состав блюда',
            'dish_type_id': dish_type_id
        }

    test_data = request.session['dish_composition_test']

    # Проверка завершения теста
    if test_data['current_index'] >= len(test_data['dish_ids']):
        result = TestResult.objects.create(
            user=request.user,
            test_type=test_data['test_type'],
            dish_type_id=test_data['dish_type_id'],
            correct=test_data['correct'],
            total=len(test_data['dish_ids'])
        )
        del request.session['dish_composition_test']
        return redirect('test_results', result_id=result.id)

    # Получаем текущее блюдо
    current_dish = Menu.objects.get(id=test_data['dish_ids'][test_data['current_index']])

    # Обработка ингредиентов
    ingredients = []
    if current_dish.compound:  # Проверяем, что compound не пустой
        ingredients = [ing.strip() for ing in current_dish.compound.split(',') if ing.strip()]

    if not ingredients:
        # Если нет ингредиентов, пропускаем блюдо
        test_data['current_index'] += 1
        request.session.modified = True
        return redirect('dish_composition_test', dish_type_id=dish_type_id)

    # Собираем случайные неправильные ингредиенты
    wrong_ingredients = []
    other_dishes = Menu.objects.filter(type_of_dish=dish_type).exclude(id=current_dish.id)
    for dish in other_dishes:
        if dish.compound:
            wrong_ingredients.extend([ing.strip() for ing in dish.compound.split(',') if ing.strip()])

    # Удаляем дубликаты и правильные ингредиенты
    wrong_ingredients = list(set(wrong_ingredients) - set(ingredients))

    # Выбираем 3-5 случайных неправильных ингредиентов
    num_wrong = min(5, len(wrong_ingredients))
    wrong_ingredients_sample = sample(wrong_ingredients, num_wrong) if num_wrong > 0 else []

    # Формируем общий список и перемешиваем
    all_ingredients = ingredients + wrong_ingredients_sample
    shuffle(all_ingredients)

    context = {
        'dish_type': dish_type,
        'target_dish': current_dish,
        'ingredients': all_ingredients,
        'correct_ingredients': ingredients,
        'current_progress': f"{test_data['current_index'] + 1}/{len(test_data['dish_ids'])}"
    }

    return render(request, 'tests/dish_composition.html', context)


@login_required
def process_dish_composition(request, dish_type_id):
    if request.method == 'POST' and 'dish_composition_test' in request.session:
        test_data = request.session['dish_composition_test']
        selected_ingredients = request.POST.getlist('ingredients')
        correct_ingredients = request.POST.getlist('correct_ingredients')

        # Проверяем, совпадают ли выбранные ингредиенты с правильными
        is_correct = (
                set(selected_ingredients) == set(correct_ingredients) and
                len(selected_ingredients) == len(correct_ingredients)
        )

        if is_correct:
            test_data['correct'] += 1

        test_data['current_index'] += 1
        request.session.modified = True

        return redirect('dish_composition_test', dish_type_id=dish_type_id)
    return redirect('mini_games')


def specialists_view(request):
    positions = Position.objects.all()
    return render(request, 'specialists.html', {'positions': positions})


def clue_view(request):
    user_position = request.user.position
    checklists = Checklist.objects.filter(position=user_position)

    return render(request, 'clue.html', {'checklists': checklists})


@login_required
def personal_view(request):
    test_results = TestResult.objects.filter(user=request.user).order_by('-date_completed')
    context = {
        'test_results': test_results
    }
    return render(request, "personal.html", context)


class CreateCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comments/create_comment.html'
    success_url = reverse_lazy('personal')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


@login_required
def test_history(request):
    results = TestResult.objects.filter(user=request.user).order_by('-date_completed')
    return render(request, 'tests/history.html', {'results': results})


def index(request):
    specialists = Account.objects.filter(position__isnull=False)
    photogallery = PhotoGallery.objects.all()
    random_photos = random.sample(list(photogallery), 3) if len(photogallery) >= 3 else photogallery
    latest_comments = Comment.objects.select_related('user').order_by('-created_at')[:6]  # Последние 6 комментариев

    return render(request, 'index.html', {
        'specialists': specialists,
        'random_photos': random_photos,
        'latest_comments': latest_comments
    })


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


def tea_game(request):
    # Фильтруем нужные типы
    types = TypeOfDish.objects.filter(name__in=["Молочные чаи", "Фруктовые чаи"])
    dishes = Menu.objects.filter(type_of_dish__in=types)

    ingredient_sets = []
    all_ingredients = set()

    # Парсим ингредиенты из поля compound
    for dish in dishes:
        ingredients = [i.strip().capitalize() for i in dish.compound.split(',') if i.strip()]
        ingredient_sets.append({
            'name': dish.name,
            'ingredients': ingredients,
            'photo': dish.photo.url if dish.photo else None
        })
        all_ingredients.update(ingredients)

    context = {
        'ingredients': sorted(all_ingredients),
        'dishes_json': json.dumps(ingredient_sets, ensure_ascii=False),
    }

    return render(request, 'tea_game.html', context)
