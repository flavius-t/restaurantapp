from django import forms
from django.forms.widgets import DateTimeInput
from .models import Ingredient, Order, MenuItem, RecipeRequirement
from django.contrib.admin.widgets import AdminSplitDateTime

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