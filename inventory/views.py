from django.shortcuts import render
from .models import Ingredient, MenuItem, RecipeRequirement, Order
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from .forms import IngredientCreateForm, IngredientUpdateForm, MenuItemCreateForm, MenuItemUpdateForm, OrderCreateForm, OrderUpdateForm, RecipeCreateForm, RecipeUpdateForm


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
    context_object_name = 'orders'
    success_url = reverse_lazy('orderlist')
    template_name = 'inventory/orderCreateForm.html'
    form_class = OrderCreateForm
    
    def post(self, request, *args, **kwargs):
        newOrder = Order.objects.create()
        newOrder.item_id = request.POST['item']
        newOrder.time = request.POST['time']
        newOrder.save()
        orders = Order.objects.raw("SELECT * FROM inventory_order")
        context = {'orderData': orders}
        menuItem = request.POST['item']
        recipereqs = RecipeRequirement.objects.raw('''SELECT * FROM inventory_reciperequirement
                                                 WHERE item_id = %s''', [menuItem])
        for item in recipereqs:
            print(item.ingredient)
        # ingredient = Ingredient.objects.raw('''SELECT * FROM inventory_ingredient 
        #                                          WHERE name = %s''', [ingredientName])
        # if ingredient:
        #     print("yes")
        # else:
        #     print("no")

        return render(request, 'inventory/orderList.html', context)
        # ingredient.quantity -= 1
        # ingredient.save()

        

class RecipeCreateView(CreateView):
    model = RecipeRequirement
    template_name = 'inventory/recipeCreateForm.html'
    form_class = RecipeCreateForm
    success_url = reverse_lazy('recipelist')

class IngredientUpdateView(UpdateView):
    model = Ingredient
    template_name = 'inventory/ingredientUpdateForm.html'
    form_class = IngredientUpdateForm
    success_url = reverse_lazy('ingredientlist')

# def IngredientUpdateView(request, ingredient):
#     name = ingredient.replace("-", " ").capitalize()
#     context = {"ingredient": name}
#     # Check if POST request
#     if request.method == "POST":
#         # Retrieve Ingredient object corresponding to name
#         ingredient = Ingredient.objects.raw('''SELECT * FROM inventory_ingredient 
#                                                 WHERE name = %s''', [name])
#         if ingredient:
#             ingredient.name = request.POST["name"]
#             ingredient.cost = request.POST["cost"]
#             ingredient.quantity = request.POST["quantity"]
#             ingredient.unit = request.POST["unit"]
#             ingredient.save()

#     return render(request, 'inventory/ingredientUpdateForm.html')


class MenuItemUpdateView(UpdateView):
    model = MenuItem
    form_class = MenuItemUpdateForm
    template_name = "inventory/menuItemUpdateForm.html"
    success_url = reverse_lazy('menuitemlist')

class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderUpdateForm
    template_name = "inventory/orderUpdateForm.html"
    success_url = reverse_lazy('orderlist')

class RecipeUpdateView(UpdateView):
    model = RecipeRequirement
    form_class = RecipeUpdateForm
    template_name = "inventory/recipeUpdateForm.html"
    success_url = reverse_lazy('recipelist')

class IngredientDeleteView(DeleteView):
    model = Ingredient
    template_name = "inventory/ingredientDeleteForm.html"
    success_url = reverse_lazy('ingredientlist')

class OrderDeleteView(DeleteView):
    model = Order
    template_name = "inventory/orderDeleteForm.html"
    success_url = reverse_lazy('orderlist')