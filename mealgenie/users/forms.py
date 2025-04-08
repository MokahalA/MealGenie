# forms.py
from django import forms
from .models import UserGrocery, GroceryCategory

class AddGroceryForm(forms.ModelForm):
    grocery_name = forms.CharField(max_length=100)
    grocery_category = forms.ModelChoiceField(queryset=GroceryCategory.objects.all())
    quantity = forms.IntegerField(min_value=1)
    unit = forms.ChoiceField(choices=UserGrocery.UNIT_CHOICES)
    expiration_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = UserGrocery
        fields = ['grocery_name', 'grocery_category', 'quantity', 'unit', 'expiration_date']

    def clean_grocery_name(self):
        grocery_name = self.cleaned_data['grocery_name'].lower()
        if not grocery_name.isalpha():
            raise forms.ValidationError('Grocery name must contain only letters')
        return grocery_name