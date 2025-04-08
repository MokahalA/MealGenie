from django.core.management.base import BaseCommand
from users.models import GroceryCategory

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        # List of categories to add
        if GroceryCategory.objects.all().exists():
            self.stdout.write(self.style.WARNING('Categories already populated. Skipping...'))
            return
        else:
            categories = [
                "Fruits", "Vegetables", "Dairy", "Meat", "Seafood",
                "Grains", "Pasta", "Baking Supplies", "Spices",
                "Beverages", "Snacks", "Frozen Foods", "Cleaning Products",
                "Toiletries", "Baby Food", "Pet Food", "Health Supplements",
                "Canned Goods", "Condiments", "Sauces", "Breakfast Cereals",
                "Nuts and Seeds", "Herbs", "Cooking Oils", "Sweets and Desserts"
            ]

            # Create categories if they don't already exist
            for category in categories:
                category, created = GroceryCategory.objects.get_or_create(category_name=category.lower())
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created category: {category}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Category: {category} already exists'))
            self.stdout.write(self.style.SUCCESS('Successfully populated the database!'))
