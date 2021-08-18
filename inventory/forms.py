from django import forms
from .models import Ingredient, Order, MenuItem, RecipeRequirement

class IngredientCreateForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ('name', 'quantity', 'unit', 'cost')