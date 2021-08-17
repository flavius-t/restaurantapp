from django.shortcuts import render
from .models import Ingredient

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