from django.shortcuts import render
from .models import Ingredient, MenuItem, RecipeRequirement, Order

# Create your views here.

# Home page
def home(request):
    return render(request, 'inventory/home.html')

def IngredientList(request):
    # SQL query to return list of all Ingredient tuples
    ingredients = Ingredient.objects.raw("SELECT * FROM inventory_ingredient")
    # 'data' is used in ingredientList.html to refer to 'ingredients'
    context = {'data': ingredients}
    return render(request, 'inventory/ingredientList.html', context)

def MenuItemList(request):
    # SQL query to return list of all MenuItem tuples
    menuItems = MenuItem.objects.raw("SELECT * FROM inventory_menuitem")
    # 'menuItemData' is used in ingredientList.html to refer to 'ingredients'
    context = {'menuItemData': menuItems}
    return render(request, 'inventory/menuItemList.html', context)