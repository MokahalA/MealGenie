"""
URL configuration for mealgenie project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from users.views import login_view, register_view, logout_view, home_view, profile_view, grocery_list_view, add_grocery_view, generate_meal_plans, get_meal_plan, edit_grocery, delete_grocery
from users.views import delete_recipe, login_view, register_view, logout_view, home_view, profile_view, grocery_list_view, add_grocery_view, generate_meal_plans, get_meal_plan, generate_recipe, save_recipe_view, get_recipes 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('home/<str:username>', home_view, name='home'),
    path('home/profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
    path('home/grocery-list/', grocery_list_view, name='grocery_list'),
    # path('home/<str:username>#my-groceries', name='my_groceries'),
    path('home/grocery-list/add', add_grocery_view, name='add_grocery'),
    path('home/getMealPlan/', get_meal_plan, name='get_meal_plan'),
    path('home/generateMealPlans/', generate_meal_plans, name='generate_meal_plans'),
    path('home/edit-grocery/<int:id>/', edit_grocery, name='edit_grocery'),
    path('home/delete-grocery/<int:id>/', delete_grocery, name='delete_grocery'),
    # path('home/track-expiration/', track_expiration, name='track_expiration')
    path('home/generateRecipe/', generate_recipe, name='generate_recipe'),
    path('home/save_recipe/', save_recipe_view, name='save_recipe'),

    path('home/getRecipes/', get_recipes, name='get_recipes'),
    path('deleteRecipe/<int:recipe_id>/', delete_recipe, name='delete_recipe'),
]