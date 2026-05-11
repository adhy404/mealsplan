from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import OperationalError

from .models import Recipe, Category, Favorite, Rating, Profile, MealPlan, MealPlanItem


# ---------------- HOME ----------------
def index(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_premium:
        recipes = Recipe.objects.all()
    else:
        recipes = Recipe.objects.filter(is_premium=False)

    favorites = []
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user)\
            .values_list('recipe_id', flat=True)

    return render(request, 'index.html', {
        'recipes': recipes,
        'favorites': favorites
    })


# ---------------- ADMIN ----------------
@login_required
def admindashboard(request):
    recipes = Recipe.objects.all()
    return render(request, 'admindashboard.html', {'recipes': recipes})


@login_required
def create_recipe(request):
    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')

        category = Category.objects.get(id=category_id)

        Recipe.objects.create(
            user=request.user,
            title=title,
            description=description,
            category=category
        )

        return redirect('index')

    return render(request, 'your_template.html', {
        'categories': categories
    })


@login_required
def edit_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)

    if request.method == "POST":
        recipe.title = request.POST.get("title")
        recipe.description = request.POST.get("description")
        recipe.ingredients = request.POST.get('ingredients')
        recipe.steps = request.POST.get('steps')

        if request.FILES.get('image'):
            recipe.image = request.FILES.get('image')

        recipe.save()
        return redirect('admindashboard')

    return render(request, "edit_recipe.html", {"recipe": recipe})


@login_required
def delete_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    recipe.delete()
    return redirect('admindashboard')


# ---------------- RECIPES ----------------
def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)

    if recipe.is_premium:
        if not request.user.is_authenticated:
            return redirect('login')

        if not hasattr(request.user, 'profile') or not request.user.profile.is_premium:
            return redirect('pricing')

    return render(request, 'recipe_detail.html', {'recipe': recipe})


def all_recipes(request):
    category_slug = request.GET.get('category')
    categories = Category.objects.all()
    recipes = Recipe.objects.all()

    if category_slug:
        recipes = recipes.filter(category__slug=category_slug)

    return render(request, "all_recipes.html", {
        "recipes": recipes,
        "categories": categories
    })


# ---------------- FAVORITES ----------------
@login_required
def toggle_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    favorite = Favorite.objects.filter(
        user=request.user,
        recipe=recipe
    ).first()

    if favorite:
        favorite.delete()
        messages.success(request, "Removed from favorites ❤️")
    else:
        profile = getattr(request.user, 'profile', None)

        if not profile or not profile.is_premium:
            total = Favorite.objects.filter(user=request.user).count()

            if total >= 5:
                messages.error(request, "Upgrade to premium 🚀")
                return redirect('pricing')

        Favorite.objects.create(user=request.user, recipe=recipe)
        messages.success(request, "Added to favorites ❤️")

    return redirect('recipe_detail', id=recipe_id)


# ---------------- RATING ----------------
@login_required
def rate_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    value = int(request.POST.get('rating', 0))

    Rating.objects.update_or_create(
        user=request.user,
        recipe=recipe,
        defaults={'value': value}
    )

    return redirect('recipe_detail', id=recipe_id)


# ---------------- PROFILE ----------------
@login_required
def profile(request):
    return render(request, 'profile.html', {
        'user': request.user,
        'recipes': Recipe.objects.filter(user=request.user),
        'favorites': Favorite.objects.filter(user=request.user)
    })


@login_required
def remove_favorite(request, recipe_id):
    Favorite.objects.filter(user=request.user, recipe_id=recipe_id).delete()
    return redirect('profile')


# ---------------- AUTH ----------------
def user_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("user_register")

        user = User.objects.create_user(
            username=username,
            email=request.POST.get("email"),
            password=request.POST.get("password")
        )

        login(request, user)
        return redirect("index")

    return render(request, "user_register.html")


def user_logout(request):
    logout(request)
    return redirect("index")


# ---------------- STATIC ----------------
def about(request):
    return render(request, 'about.html')


def pricing(request):
    return render(request, 'pricing.html')



# ---------------- PREMIUM ----------------
@login_required
def upgrade(request):
    profile = request.user.profile
    profile.is_premium = True
    profile.save()
    return redirect('index')


# ---------------- PAYMENTS ----------------
def payment_page(request):
    if request.method == "POST":
        return redirect("payment_success")
    return render(request, "payment.html")


def payment_success(request):
    return render(request, "payment_success.html")


def upgrade_success(request):
    return render(request, "upgrade_success.html")


def checkout(request):
    if request.method == "POST":
        return redirect("payment_processing")
    return render(request, "checkout.html")


def payment_processing(request):
    return render(request, "payment_processing.html")


# ---------------- MEAL PLANNER ----------------
@login_required
def my_plans(request):
    plans = MealPlan.objects.filter(user=request.user)
    return render(request, 'meal_plans.html', {'plans': plans})


@login_required
def create_plan(request):
    if request.method == 'POST':
        name = request.POST.get('name')

        if name:
            plan = MealPlan.objects.create(name=name, user=request.user)
            return redirect('edit_plan', id=plan.id)

    return render(request, 'create_plan.html')


@login_required
def edit_plan(request, id):
    plan = get_object_or_404(MealPlan, id=id, user=request.user)
    recipes = Recipe.objects.all()

    if request.method == 'POST':
        MealPlanItem.objects.create(
            plan=plan,
            day=request.POST.get('day'),
            meal_type=request.POST.get('meal_type'),
            recipe_id=request.POST.get('recipe')
        )
        return redirect('edit_plan', id=plan.id)

    return render(request, 'edit_plan.html', {
        'plan': plan,
        'recipes': recipes,
        'items': MealPlanItem.objects.filter(plan=plan)
    })


@login_required
def view_plan(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
    return render(request, 'view_plan.html', {
        'plan': plan,
        'items': MealPlanItem.objects.filter(plan=plan)
    })


@login_required
def grocery_list(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
    items = MealPlanItem.objects.filter(plan=plan)

    ingredients = []
    for item in items:
        if item.recipe.ingredients:
            ingredients += item.recipe.ingredients.split(',')

    return render(request, 'grocery_list.html', {
        'plan': plan,
        'ingredients': ingredients
    })


# ---------------- AI SUGGEST ----------------
def suggest_meals(request):
    recipes = Recipe.objects.filter(description__icontains='protein')

    return render(request, 'suggestions.html', {
        'recipes': recipes
    })



def add_recipe(request):
    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        ingredients = request.POST.get('ingredients')
        steps = request.POST.get('steps')
        cooking_time = request.POST.get('cooking_time')
        servings = request.POST.get('servings')
        image = request.FILES.get('image')

        error = None

        # ✅ Validate servings
        try:
            servings = int(servings)
        except (ValueError, TypeError):
            error = "Servings must be a valid number."

        # ✅ Validate cooking_time (optional but smart)
        try:
            cooking_time = int(cooking_time)
        except (ValueError, TypeError):
            error = "Cooking time must be a valid number."

        # ✅ Validate category
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            error = "Invalid category selected."

        # 🚨 If any error → show form again
        if error:
            return render(request, 'add_recipe.html', {
                'categories': categories,
                'error': error
            })

        # ✅ Save safely
        Recipe.objects.create(
            user=request.user if request.user.is_authenticated else None,
            category=category,
            title=title,
            description=description,
            ingredients=ingredients,
            steps=steps,
            cooking_time=cooking_time,
            servings=servings,
            image=image
        )

        return redirect('index')

    return render(request, 'add_recipe.html', {
        'categories': categories
    })