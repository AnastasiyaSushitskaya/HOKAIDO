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


def login_view(request):
    return render(request, "login.html")


def schedule_view(request):
    last_file = ExcelFile.objects.last()
    latest_comments = Comment.objects.select_related('user').order_by('-created_at')[:6]

    context = {
        'last_file': last_file,
        'latest_comments': latest_comments
    }
    return render(request, 'schedule.html', context)


def menu_view(request):
    types_of_dish = TypeOfDish.objects.prefetch_related('menus').all()
    return render(request, 'menu.html', {'types_of_dish': types_of_dish})


@login_required
def mini_games_view(request):
    all_dish_types = TypeOfDish.objects.all()

    if request.user.is_superuser:
        dish_types = all_dish_types
    else:

        user_position = request.user.position

        available_dish_types = PositionTypeOfDish.objects.filter(
            position=user_position
        ).values_list('dish_type', flat=True)

        dish_types = all_dish_types.filter(id__in=available_dish_types)

    context = {
        'dish_types': dish_types,
    }
    return render(request, 'mini-games.html', context)


@login_required
def guess_dish_test(request, dish_type_id):
    dish_type = get_object_or_404(TypeOfDish, id=dish_type_id)

    if 'test_data' not in request.session:
        request.session['test_data'] = {
            'dish_ids': list(Menu.objects.filter(type_of_dish=dish_type).values_list('id', flat=True)),
            'current_index': 0,
            'correct': 0,

            'test_type': 'Угадай блюдо',
            'dish_type_id': dish_type_id
        }

    test_data = request.session['test_data']

    if test_data['current_index'] >= len(test_data['dish_ids']):
        result = TestResult.objects.create(
            user=request.user,
            test_type=test_data['test_type'],
            dish_type_id=test_data['dish_type_id'],
            correct=test_data['correct'],
            total=len(test_data['dish_ids'])
        )
        del request.session['test_data']
        return redirect('test_results', result_id=result.id)

    current_dish = Menu.objects.get(id=test_data['dish_ids'][test_data['current_index']])

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
        confirmed = request.POST.get('confirmed', 'false') == 'true'

        if confirmed and user_answer == correct_answer:
            test_data['correct'] += 1

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
        return redirect('mini_games')


@login_required
def missing_ingredient_test(request, dish_type_id):
    dish_type = get_object_or_404(TypeOfDish, id=dish_type_id)

    if 'missing_ingredient_test' not in request.session:
        request.session['missing_ingredient_test'] = {
            'dish_ids': list(Menu.objects.filter(type_of_dish=dish_type).values_list('id', flat=True)),
            'current_index': 0,
            'correct': 0,
            'test_type': 'Недостающий ингредиент',
            'dish_type_id': dish_type_id
        }

    test_data = request.session['missing_ingredient_test']

    if test_data['current_index'] >= len(test_data['dish_ids']):
        result = TestResult.objects.create(
            user=request.user,
            test_type=test_data['test_type'],
            dish_type_id=test_data['dish_type_id'],
            correct=test_data['correct'],
            total=len(test_data['dish_ids'])
        )

        request.session['test_result_id'] = result.id
        del request.session['missing_ingredient_test']
        request.session.modified = True
        return redirect('test_results', result_id=result.id)

    current_dish = Menu.objects.get(id=test_data['dish_ids'][test_data['current_index']])

    ingredients = [ing.strip() for ing in current_dish.compound.split(',') if ing.strip()]

    if not ingredients:
        test_data['current_index'] += 1
        request.session.modified = True
        return redirect('missing_ingredient_test', dish_type_id=dish_type_id)

    hidden_ingredient = random.choice(ingredients)

    hidden_index = ingredients.index(hidden_ingredient)
    display_ingredients = ingredients.copy()
    display_ingredients[hidden_index] = '...'
    display_compound = ', '.join(display_ingredients)

    correct_answer = hidden_ingredient
    other_ingredients = []

    other_dishes = Menu.objects.filter(type_of_dish=dish_type).exclude(id=current_dish.id)
    for dish in other_dishes:
        if dish.compound:
            other_ingredients.extend([ing.strip() for ing in dish.compound.split(',') if ing.strip()])

    other_ingredients = list(set(other_ingredients))
    if correct_answer in other_ingredients:
        other_ingredients.remove(correct_answer)

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

    if 'dish_composition_test' not in request.session:
        request.session['dish_composition_test'] = {
            'dish_ids': list(Menu.objects.filter(type_of_dish=dish_type).values_list('id', flat=True)),
            'current_index': 0,
            'correct': 0,
            'test_type': 'Состав блюда',
            'dish_type_id': dish_type_id
        }

    test_data = request.session['dish_composition_test']

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

    current_dish = Menu.objects.get(id=test_data['dish_ids'][test_data['current_index']])

    ingredients = []
    if current_dish.compound:
        ingredients = [ing.strip() for ing in current_dish.compound.split(',') if ing.strip()]

    if not ingredients:
        test_data['current_index'] += 1
        request.session.modified = True
        return redirect('dish_composition_test', dish_type_id=dish_type_id)

    wrong_ingredients = []
    other_dishes = Menu.objects.filter(type_of_dish=dish_type).exclude(id=current_dish.id)
    for dish in other_dishes:
        if dish.compound:
            wrong_ingredients.extend([ing.strip() for ing in dish.compound.split(',') if ing.strip()])

    wrong_ingredients = list(set(wrong_ingredients) - set(ingredients))

    num_wrong = min(5, len(wrong_ingredients))
    wrong_ingredients_sample = sample(wrong_ingredients, num_wrong) if num_wrong > 0 else []

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

    return render(request, 'index.html', {
        'specialists': specialists,
        'random_photos': random_photos,
    })


def edit_excel(request, file_id):
    excel_file = ExcelFile.objects.get(id=file_id)
    df = excel_file.get_excel_data()

    if request.method == 'POST':
        updated_data = request.POST.getlist('data')

        df.iloc[:, :] = updated_data
        df.to_excel(excel_file.file.path, index=False)

        return redirect('success_url')

    context = {
        'excel_file': excel_file,
        'data': df.values.tolist(),
    }
    return render(request, 'edit_excel.html', context)


def tea_game(request):
    types = TypeOfDish.objects.filter(name__in=["Молочные чаи", "Фруктовые чаи"])
    dishes = Menu.objects.filter(type_of_dish__in=types)

    ingredient_sets = []
    all_ingredients = set()

    for dish in dishes:
        ingredients = [i.strip().capitalize() for i in dish.compound.split(',') if i.strip()]
        ingredient_sets.append({
            'name': dish.name,
            'ingredients': ingredients,
            'photo': dish.photo.url if dish.photo else None
        })
        all_ingredients.update(ingredients)

    target_dish = random.choice(ingredient_sets) if ingredient_sets else None

    context = {
        'ingredients': sorted(all_ingredients),
        'dishes_json': json.dumps(ingredient_sets, ensure_ascii=False),
        'target_dish': target_dish,
        'target_dish_json': json.dumps(target_dish, ensure_ascii=False) if target_dish else None,
    }

    return render(request, 'tea_game.html', context)


def gunkan_game(request):
    types = TypeOfDish.objects.filter(name="Гунканы")
    dishes = Menu.objects.filter(type_of_dish__in=types)

    ingredient_sets = []
    all_ingredients = set()

    for dish in dishes:
        ingredients = [i.strip().capitalize() for i in dish.compound.split(',') if i.strip()]
        ingredient_sets.append({
            'name': dish.name,
            'ingredients': ingredients,
            'photo': dish.photo.url if dish.photo else None
        })
        all_ingredients.update(ingredients)

    # Выбираем случайный гункан для задания
    target_dish = random.choice(ingredient_sets) if ingredient_sets else None

    context = {
        'ingredients': sorted(all_ingredients),
        'dishes_json': json.dumps(ingredient_sets, ensure_ascii=False),
        'target_dish': target_dish,
        'target_dish_json': json.dumps(target_dish, ensure_ascii=False) if target_dish else None,
    }

    return render(request, 'gunkan_game.html', context)


def test_results_view(request):
    test_types = TestResult.objects.values_list('test_type', flat=True).distinct().order_by('test_type')

    users = Account.objects.filter(testresult__isnull=False).distinct().order_by('username')

    results = TestResult.objects.select_related('user', 'dish_type').all()

    user_filter = request.GET.get('user')
    test_type_filter = request.GET.get('test_type')

    if user_filter:
        results = results.filter(user_id=user_filter)

    if test_type_filter:
        results = results.filter(test_type=test_type_filter)

    results = results.order_by('-date_completed').distinct()

    context = {
        'test_results': results,
        'test_types': test_types,
        'users': users,
        'selected_user': user_filter,
        'selected_test_type': test_type_filter,
    }

    return render(request, 'test_results.html', context)
