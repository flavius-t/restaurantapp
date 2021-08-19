from django.shortcuts import render
from .models import Ingredient, MenuItem, RecipeRequirement, Order
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from .forms import IngredientCreateForm, MenuItemCreateForm, OrderCreateForm, RecipeCreateForm

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
    # 'menuItemData' is used in menuItemList.html to refer to 'menuItems'
    context = {'menuItemData': menuItems}
    return render(request, 'inventory/menuItemList.html', context)

def OrderList(request):
    # SQL query to return list of all Order tuples
    orders = Order.objects.raw("SELECT * FROM inventory_order")
    # 'orderData' is used in orderList.html to refer to 'orders'
    context = {'orderData': orders}
    return render(request, 'inventory/orderList.html', context)

def RecipeRequirementList(request):
    # SQL query to return all RecipeRequirement tuples related to input MenuItem
    menuItems = MenuItem.objects.raw("SELECT * FROM inventory_menuitem")
    # 'recipeData' is used in recipeRequirementList.html to refer to 'recipe'
    context = {
            'menuItemData': menuItems,
            }

    # validate if GET object exists
    if request.GET.get('menuItems'):
        # retrieve menuItem selected by user in dropdown menu
        item = request.GET['menuItems']
        # SQL query to find all Ingredients related to menuItem
        recipeRequirements = RecipeRequirement.objects.raw('''SELECT * FROM inventory_reciperequirement 
                                                            WHERE item_id = %s''', [item])
        context = {
            'menuItemData': menuItems,
            'recipeData': recipeRequirements,
            }

    return render(request, 'inventory/recipeRequirementList.html', context)

class IngredientCreateView(CreateView):
    model = Ingredient
    success_url = reverse_lazy('ingredientlist')
    template_name = 'inventory/ingredientCreateForm.html'
    form_class = IngredientCreateForm

class MenuItemCreateView(CreateView):
    model = MenuItem
    success_url = reverse_lazy('menuitemlist')
    template_name = 'inventory/menuItemCreateForm.html'
    form_class = MenuItemCreateForm

class OrderCreateView(CreateView):
    model = Order
    success_url = reverse_lazy('orderlist')
    template_name = 'inventory/orderCreateForm.html'
    form_class = OrderCreateForm

class RecipeCreateView(CreateView):
    model = RecipeRequirement
    template_name = 'inventory/recipeCreateForm.html'
    form_class = RecipeCreateForm
    success_url = reverse_lazy('recipecreate')