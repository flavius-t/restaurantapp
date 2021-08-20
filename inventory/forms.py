from django import forms
from django.forms.widgets import DateTimeInput
from .models import Ingredient, Order, MenuItem, RecipeRequirement

class IngredientCreateForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ('name', 'quantity', 'unit', 'cost')

class MenuItemCreateForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ('name', 'cost')

# date-time widget for use with OrderCreateForm
class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('time', 'item')
        widgets = {
            'time': DateTimeInput(),
        }

class RecipeCreateForm(forms.ModelForm):
    class Meta:
        model = RecipeRequirement
        fields = ('item', 'ingredient', 'quantity')

class IngredientUpdateForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ('name', 'quantity', 'unit', 'cost')

class MenuItemUpdateForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ('name', 'cost')

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('item', 'time')
        widgets = {
            'time': DateTimeInput(),
        }