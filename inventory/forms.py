from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.forms.widgets import DateTimeInput
from .models import Ingredient, Order, MenuItem, RecipeRequirement
from django.contrib.auth.forms import UserCreationForm

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


class RecipeUpdateForm(forms.ModelForm):
    class Meta:
        model = RecipeRequirement
        fields = ('ingredient', 'quantity')

class EditUserForm(UserChangeForm):
    email = forms.EmailField(widget=forms.EmailInput())
    first_name = forms.CharField(max_length=100, widget=forms.TextInput())
    last_name = forms.CharField(max_length=100, widget=forms.TextInput())
    password = None
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

class UserSignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.fields['username'].widget.attrs.update({ 
            'class': 'form-input', 
            'required':'', 
            'name':'username', 
            'id':'username', 
            'type':'text', 
            'placeholder':'Username', 
            'maxlength': '16', 
            'minlength': '6', 
            }) 
        self.fields['email'].widget.attrs.update({ 
            'class': 'form-input', 
            'required':'', 
            'name':'email', 
            'id':'email', 
            'type':'email', 
            'placeholder':'Email', 
            }) 
        self.fields['password1'].widget.attrs.update({ 
            'class': 'form-input', 
            'required':'', 
            'name':'password1', 
            'id':'password1', 
            'type':'password', 
            'placeholder':'Password', 
            'maxlength':'22',  
            'minlength':'8' 
            }) 
        self.fields['password2'].widget.attrs.update({ 
            'class': 'form-input', 
            'required':'', 
            'name':'password2', 
            'id':'password2', 
            'type':'password', 
            'placeholder':'Confirm password', 
            'maxlength':'22',  
            'minlength':'8' 
            }) 
 
    username = forms.CharField(max_length=20, label=False) 
    email = forms.EmailField(max_length=100) 

    class meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
