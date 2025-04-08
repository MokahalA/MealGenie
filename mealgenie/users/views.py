# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile, UserGrocery, GroceryCategory, MealPlans, Recipe
from django.urls import reverse
from django.http import JsonResponse
import json
from .forms import AddGroceryForm
from .utils import prompt_ollama
from datetime import timedelta
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home', username=user.username)
        else:
            context = {'error': 'Invalid username or password'}
            return render(request, 'login.html', context)
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        login(request, user)
        return redirect('home', username=user.username)
    return render(request, 'register.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request, username):
    user = User.objects.get(username=username)
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    context = {
        'first_name': user.first_name,
        'username': user.username,
        'dietary_preferences': profile.dietary_preferences,
        'allergies': profile.allergies
    }
    return render(request, 'home.html', context)

@login_required
def profile_view(request):
    # Ensure the user profile exists
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "GET":
        user = request.user
        dietary_preferences = json.loads(profile.dietary_preferences) if profile.dietary_preferences else []
        allergies = json.loads(profile.allergies) if profile.allergies else []

        return JsonResponse({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "dietary_preferences": dietary_preferences,
            "allergies": allergies
        })

    elif request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                
                # Update first name and last name
                if 'first_name' in data:
                    request.user.first_name = data['first_name']
                if 'last_name' in data:
                    request.user.last_name = data['last_name']
                request.user.save()

                # Update dietary preferences
                if 'dietary_preferences' in data:
                    profile.dietary_preferences = json.dumps(data['dietary_preferences'])
                    profile.save()

                # Update allergies
                if 'allergies' in data:
                    profile.allergies = json.dumps(data['allergies'])
                    profile.save()

                return JsonResponse({'status': 'success'}, status=200)
                
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    # Convert JSON strings back to lists for rendering in the context
    preferences_list = json.loads(profile.dietary_preferences) if profile.dietary_preferences else []
    allergies_list = json.loads(profile.allergies) if profile.allergies else []

    context = {
        'user': request.user,
        'preferences_json': json.dumps(preferences_list),
        'allergies_json': json.dumps(allergies_list),
    }
    return render(request, 'profile.html', context)

@login_required
def grocery_list_view(request):
    if request.method == 'GET':
        sort_by = request.GET.get('sort_by', 'category')  # Default to category
        order = request.GET.get('order', 'asc')  # Default to ascending order
        days = request.GET.get('days', None)  # Default to 7 days

        user_groceries = UserGrocery.objects.filter(user=request.user)
        if days:
            expiration_threshold = now().date() + timedelta(days=int(days))
            user_groceries = user_groceries.filter(expiration_date__lte=expiration_threshold)

        if sort_by == 'expiration_date':
            if order == 'asc':
                user_groceries = user_groceries.order_by('expiration_date')
            else:
                user_groceries = user_groceries.order_by('-expiration_date')
        elif sort_by == 'category':
            if order == 'asc':
                user_groceries = user_groceries.order_by('grocery_category')
            else:
                user_groceries = user_groceries.order_by('-grocery_category')


        print(user_groceries)

        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            grocery_list = [{
                'id': item.id,
                'name': item.grocery_name.capitalize(),
                'category': item.grocery_category.category_name.capitalize(),
                'quantity': item.quantity,
                'unit': item.unit,
                'expiration_date': item.expiration_date.strftime('%Y-%m-%d') if item.expiration_date else None
            } for item in user_groceries]
            return JsonResponse({'groceries': grocery_list})
    return render(request, 'grocery_list.html')

@login_required
def add_grocery_view(request):
    if request.method == 'POST':
        form = AddGroceryForm(request.POST)
        if form.is_valid():
            grocery = form.save(commit=False)
            grocery.user = request.user
            grocery.save()
            return redirect(f"{reverse('home', args=[request.user.username])}#my-groceries")
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form'}, status=400)
    if request.method == 'GET':
        form = AddGroceryForm()
        return render(request, 'add_grocery.html', {'form': form})
    

@login_required
def generate_meal_plans(request):
    if request.method == "POST":
        # Obtain the user's profile to get dietary preferences and allergies
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        dietary_preferences = json.loads(profile.dietary_preferences) if profile.dietary_preferences else []
        allergies = json.loads(profile.allergies) if profile.allergies else []

        # Create the prompt for the model
        if not dietary_preferences and not allergies:
            prompt = (
                "Generate a meal plan of breakfast, lunch, dinner for 7 days. "
                "Name them using Day 1, Day 2, etc. No recipes, just the names of the meals."
            )
        else:
            prompt = (
                "Generate a meal plan of breakfast, lunch, dinner for 7 days. "
                "Name them using Day 1, Day 2, etc. No recipes, just the names of the meals. "
                "It should be free of: "
            )
            prompt += ", ".join(allergies) + ". "
            prompt += "It should be " + ", ".join(dietary_preferences) + "."

        try:
            # Call the model to generate the meal plan
            result = prompt_ollama(prompt, model="llama3.2:3b")  # Replace `prompt_ollama` with your model function

            # Save or overwrite the user's meal plan in the database
            meal_plan_obj, _ = MealPlans.objects.get_or_create(user=request.user)
            meal_plan_obj.meal_plan = result
            meal_plan_obj.save()

            # Return the generated meal plan as JSON
            return JsonResponse({
                'dietary_preferences': dietary_preferences,
                'allergies': allergies,
                'response': result,
                'message': 'Meal plan successfully generated and saved!'
            })

        except Exception as e:
            # Handle errors in meal plan generation or saving
            return JsonResponse({
                'error': 'An error occurred while generating the meal plan.',
                'details': str(e)
            }, status=500)
    
    else:
        # Return an error for unsupported HTTP methods
        return JsonResponse({'error': 'Invalid request method. Use POST instead.'}, status=405)

@login_required
def get_meal_plan(request):
    try:
        meal_plan_obj = MealPlans.objects.filter(user=request.user).first()
        if meal_plan_obj:
            dietary_preferences = []
            allergies = []

            # Fetch dietary preferences and allergies from the user profile
            profile = UserProfile.objects.filter(user=request.user).first()
            if profile:
                dietary_preferences = json.loads(profile.dietary_preferences) if profile.dietary_preferences else []
                allergies = json.loads(profile.allergies) if profile.allergies else []

            return JsonResponse({
                'response': meal_plan_obj.meal_plan,
                'dietary_preferences': dietary_preferences,
                'allergies': allergies,
                'message': 'Meal plan fetched successfully!'
            })
        else:
            return JsonResponse({
                'response': '',
                'message': 'No meal plan found for the user.',
            }, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
@csrf_exempt
def edit_grocery(request, id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            grocery = get_object_or_404(UserGrocery, id=id)
            grocery.name = data.get('name', grocery.grocery_name)
            grocery.category = data.get('category', grocery.grocery_category)
            grocery.quantity = data.get('quantity', grocery.quantity)
            grocery.unit = data.get('unit', grocery.unit)
            grocery.expiration_date = data.get('expiration_date', grocery.expiration_date)
            grocery.save()
            return JsonResponse({'message': 'Grocery updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@csrf_exempt
def delete_grocery(request, id):
    if request.method == 'DELETE' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            grocery = get_object_or_404(UserGrocery, id=id)
            grocery.delete()
            return JsonResponse({'message': 'Grocery deleted successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

# def track_expiration(request):
#     days = int(request.GET.get('days', 7))  # Default to 7 days
#     expiration_threshold = now().date() + timedelta(days=days)

#     expiring_groceries = UserGrocery.objects.filter(user=request.user).filter(expiration_date__lte=expiration_threshold)

#     grocery_list = [{
#                 'id': item.id,
#                 'name': item.grocery_name.capitalize(),
#                 'category': item.grocery_category.category_name.capitalize(),
#                 'quantity': item.quantity,
#                 'unit': item.unit,
#                 'expiration_date': item.expiration_date.strftime('%Y-%m-%d') if item.expiration_date else None
#             } for item in expiring_groceries]
#     return JsonResponse({'groceries': grocery_list})

@login_required
def generate_recipe(request):
    if request.method == 'POST':
        # Parse JSON request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)

        # Obtain allergies and preferences saved in the user profile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        dietary_preferences = json.loads(profile.dietary_preferences) if profile.dietary_preferences else []
        allergies = json.loads(profile.allergies) if profile.allergies else []

        # Get cuisine and pantry preference from request
        cuisine = data.get('cuisine', 'None')

        # Initialize prompt and build dynamically
        prompt = "Always use all of these labels in your response: Name, Ingredients, Steps. Do not provide any extra information. Do not use any styling in your response."

        if cuisine != "None":
            prompt += f"Generate a recipe for a dish in the {cuisine} cuisine. "
        else:
            prompt += "Generate a recipe for a dish from any cuisine. "

        if dietary_preferences:
            prompt += f"Ensure the recipe adheres to the following dietary preferences: {', '.join(dietary_preferences)}. "

        if allergies:
            prompt += f"Avoid using ingredients that include the following allergens: {', '.join(allergies)}. "

        # Loop until the response contains the necessary information
        while True:
            try:
                result = prompt_ollama(prompt, model="llama3.2:3b")  # Replace with actual AI function call

                # Remove all '*' characters from the result
                result = result.replace('*', '')

                # Ensure the result contains all the necessary labels
                if "Name:" in result and "Ingredients:" in result and "Steps:" in result:
                    # Split the result into parts based on labels
                    parts = result.split('Name: ')[1:]  # Skip the initial empty string before 'Name'

                    recipe_details = []
                    for part in parts:
                        # Extract Name, Ingredients, and Steps
                        name = part.split('Ingredients:')[0].strip()
                        ingredients_and_steps = part.split('Ingredients:')[1].split('Steps:')
                        ingredients = ingredients_and_steps[0].strip()
                        steps = ingredients_and_steps[1].strip() if len(ingredients_and_steps) > 1 else ""

                        # Store them in an array
                        recipe_details.append({
                            'name': name,
                            'ingredients': ingredients,
                            'steps': steps,
                            'promptResult': result,
                            'dietary_preferences': dietary_preferences,
                            'allergies': allergies,
                        })

                    return JsonResponse({
                        'response': result,  # This is the prompt response
                        'recipe': recipe_details,  # This is the parsed recipe details object
                        'message': 'Recipe successfully generated!'
                    })
                else:
                    # Reprompt if any of the necessary labels are missing
                    continue

            except Exception as e:
                return JsonResponse({'error': f'Error generating recipe: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def save_recipe_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recipe_title = data.get('recipe_title')
            ingredients = data.get('ingredients')
            steps = data.get('steps')

            if not recipe_title or not ingredients or not steps:
                return JsonResponse({'error': 'All fields are required'}, status=400)

            # Save recipe
            Recipe.objects.create(
                user=request.user,
                recipe_title=recipe_title,
                ingredients=ingredients,
                steps=steps
            )
            return JsonResponse({'message': 'Recipe saved successfully'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@login_required
def get_recipes(request):
    if request.method == 'GET':
        recipes = Recipe.objects.filter(delete_flag=0, user=request.user)
        recipe_list = [{
            'id': recipe.recipe_id,
            'name': recipe.recipe_title,
            'ingredients': recipe.ingredients,
            'steps': recipe.steps
        } for recipe in recipes]
        return JsonResponse({'recipes': recipe_list})
    return JsonResponse({'error': 'Invalid request method. Only GET is allowed.'}, status=405)

@login_required
def delete_recipe(request, recipe_id):
    if request.method == 'DELETE':
        # Retrieve the recipe and ensure it belongs to the logged-in user
        recipe = get_object_or_404(Recipe, pk=recipe_id, user=request.user)

        # Mark the recipe as deleted instead of deleting it
        recipe.delete_flag = 1
        recipe.save()

        return JsonResponse({'message': 'Recipe marked as deleted.'}, status=200)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)
