from django.contrib.auth.models import User
from django.db import models

# Extending the User model with a one-to-one relationship to store additional user information.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dietary_preferences = models.TextField(blank=True)
    allergies = models.TextField(blank=True)

class MealPlans(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Enforce one plan per user
    meal_plan = models.TextField(blank=True)

class GroceryCategory(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name.capitalize()

# class Grocery(models.Model):
#     # Define choices as class constants
#     LB = 'lb'
#     KG = 'kg'
#     UNIT = 'unit(s)'
    
#     UNIT_CHOICES = [
#         (LB, 'Pound'),
#         (KG, 'Kilogram'),
#         (UNIT, 'Unit(s)'),
#     ]

#     grocery_id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=100)
#     price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
#     category = models.ForeignKey(GroceryCategory, on_delete=models.CASCADE)
#     unit = models.CharField(
#         max_length=10,
#         choices=UNIT_CHOICES,
#         default=UNIT
#     )
#     # image = models.ImageField(upload_to='grocery_images', blank=True)

#     def __str__(self):
#         return f"{self.name.capitalize()} ({self.category.category_name.capitalize()})"


class UserGrocery(models.Model):
    # Define choices as class constants
    LB = 'lb'
    KG = 'kg'
    UNIT = 'unit(s)'
    
    UNIT_CHOICES = [
        (LB, 'Pound'),
        (KG, 'Kilogram'),
        (UNIT, 'Unit(s)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grocery_name = models.CharField(max_length=100)
    grocery_category = models.ForeignKey(GroceryCategory, on_delete=models.CASCADE, default=1)
    quantity = models.IntegerField()
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default=UNIT
    )
    expiration_date = models.DateField(blank=True, null=True)

class Recipe(models.Model):
    recipe_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_title = models.CharField(max_length=255)
    ingredients = models.TextField()
    steps = models.TextField()
    delete_flag = models.IntegerField(default=0)

    def __str__(self):
        return self.recipe_title