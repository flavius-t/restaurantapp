from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.forms.widgets import DateTimeInput
from .models import Ingredient, Order, MenuItem, RecipeRequirement
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm

class IngredientCreateForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ('name', 'quantity', 'unit', 'cost')
        widgets = ({
            'name': forms.TextInput(attrs={'class': 'form-input', 'id':'form-input', 'placeholder': 'Name'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'id':'form-input', 'placeholder': 'Quantity'}),
            'unit': forms.TextInput(attrs={'class': 'form-input', 'id':'form-input', 'placeholder': 'Unit'}),
            'cost': forms.NumberInput(attrs={'class': 'form-input', 'id':'form-input', 'placeholder': 'Cost'}),
        })

class MenuItemCreateForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ('name', 'cost')
        widgets = ({
            'name': forms.TextInput(attrs={'class': 'form-input', 'id':'form-input', 'placeholder': 'Menu Item Name'}),
            'cost': forms.NumberInput(attrs={'class': 'form-input', 'id':'form-input', 'placeholder': 'Item Cost'}),
        })

# date-time widget for use with OrderCreateForm
class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('time', 'item')
        widgets = {
            'time': DateTimeInput(attrs={'class': 'form-input', 'id':'form-input', 'placeholder': 'Date-Time'}),
            'item': forms.SelectMultiple(attrs={'class': 'form-input', 'id':'form-input', 'placeholder': 'Menu Items'})
        }

class RecipeCreateForm(forms.ModelForm):
    class Meta:
        model = RecipeRequirement
        fields = ('item', 'ingredient', 'quantity')
        widgets = ({
            'item': forms.Select(attrs={'class': 'form-input', 'id':'form-input', 'placeholder': 'Menu Item Name'}),
            'ingredient': forms.Select(attrs={'class': 'form-input', 'id':'form-input', 'placeholder': 'Required Ingredient'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'id':'form-input', 'placeholder': 'Quantity'})
        })

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
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    password = None

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({ 
            'class': 'form-input', 
            'id': 'form-input',
            'placeholder':'Email',   
            })
        self.fields['first_name'].widget.attrs.update({ 
            'class': 'form-input', 
            'id': 'form-input',
            'placeholder':'First Name',
            })
        self.fields['last_name'].widget.attrs.update({ 
            'class': 'form-input', 
            'id': 'form-input',
            'placeholder':'Last Name',
            })
        

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

class UserLoginForm(AuthenticationForm):
    # class Meta:
    #     widgets = {
    #         'username': forms.TextInput(attrs={'class': 'form-input'}),
    #         'password': forms.PasswordInput(attrs={'class': 'form-input'})
    #     }

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({ 
            'class': 'form-input', 
            'id': 'form-input',
            'placeholder':'Username',   
            })
        self.fields['password'].widget.attrs.update({ 
            'class': 'form-input', 
            'id': 'form-input',
            'placeholder':'Password',
            }) 
    
    # username = forms.CharField(max_length=22)
    # password = forms.PasswordInput()

# subclass PasswordChangeForm to enable custom CSS form
class ChangePassword(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']
    
    def __init__(self, *args, **kwargs):
        super(ChangePassword, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-input',
            'id': 'form-input',
            'placeholder': 'Old Password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-input',
            'id': 'form-input',
            'placeholder': 'New Password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-input',
            'id': 'form-input',
            'placeholder': 'Confirm New Password'
        })
        
    