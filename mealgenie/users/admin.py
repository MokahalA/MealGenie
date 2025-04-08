from django.contrib import admin
from users.models import UserProfile, GroceryCategory, UserGrocery

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'dietary_preferences', 'allergies']

class GroceryCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name']

# class GroceryAdmin(admin.ModelAdmin):
#     list_display = ['name', 'price', 'category', 'unit']
#     def get_category_name(self, obj):
#         return obj.category.category_name
#     get_category_name.short_description = 'Category'  # Column header in admin
    
#     # Add search and filter capabilities
#     search_fields = ['name']
#     list_filter = ['category']

class UserGroceryAdmin(admin.ModelAdmin):
    list_display = ['user', 'grocery_name', 'grocery_category', 'quantity', 'unit', 'expiration_date']
    def get_category_name(self, obj):
        return obj.grocery_category.category_name
    get_category_name.short_description = 'Category'  # Column header in admin
    # Add search and filter capabilities
    search_fields = ['user']
    list_filter = ['user']

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(GroceryCategory, GroceryCategoryAdmin)
# admin.site.register(Grocery, GroceryAdmin)
admin.site.register(UserGrocery, UserGroceryAdmin)
