from django.urls import path
from . import views

urlpatterns = [

    # ---------------- HOME ----------------
    path('', views.index, name='index'),

    # ---------------- RECIPES ----------------
    path('recipes/', views.all_recipes, name='all_recipes'),
    path('recipe/<int:id>/', views.recipe_detail, name='recipe_detail'),

    # ---------------- ADMIN ----------------
    path('admindashboard', views.admindashboard, name='admindashboard'),
    path('add-recipe/', views.add_recipe, name='add_recipe'),
    path('edit-recipe/<int:id>/', views.edit_recipe, name='edit_recipe'),
    path('delete-recipe/<int:id>/', views.delete_recipe, name='delete_recipe'),

    # ---------------- FAVORITES ----------------
    path('favorite/<int:recipe_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('remove-favorite/<int:recipe_id>/', views.remove_favorite, name='remove_favorite'),

    # ---------------- RATING ----------------
    path('rate/<int:recipe_id>/', views.rate_recipe, name='rate_recipe'),

    # ---------------- PROFILE ----------------
    path('profile/', views.profile, name='profile'),

    # ---------------- AUTH ----------------
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='logout'),

    # ---------------- STATIC ----------------
    path('about/', views.about, name='about'),

    # ---------------- PREMIUM ----------------
    path('pricing/', views.pricing, name='pricing'),
    path('upgrade/', views.upgrade, name='upgrade'),

    # ---------------- PAYMENTS ----------------
    path('payment/', views.payment_page, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('upgrade-success/', views.upgrade_success, name='upgrade_success'),
    path('checkout/', views.checkout, name='checkout'),
    path('processing/', views.payment_processing, name='payment_processing'),

    # ---------------- MEAL PLANNER ----------------
    path('meal-plans/', views.my_plans, name='my_plans'),
    path('create-plan/', views.create_plan, name='create_plan'),
    path('edit-plan/<int:id>/', views.edit_plan, name='edit_plan'),
    path('view-plan/<int:plan_id>/', views.view_plan, name='view_plan'),
    path('grocery/<int:plan_id>/', views.grocery_list, name='grocery_list'),

    # ---------------- AI ----------------
    path('suggest/', views.suggest_meals, name='suggest_meals'),
]