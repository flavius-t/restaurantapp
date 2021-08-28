from django.shortcuts import render, redirect
from .models import Ingredient, MenuItem, RecipeRequirement, Order
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from .forms import IngredientCreateForm, IngredientUpdateForm, MenuItemCreateForm, MenuItemUpdateForm, OrderCreateForm, OrderUpdateForm, RecipeCreateForm, RecipeUpdateForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

# Home page
@login_required
def home(request):
    context = {'name': request.user}
    return render(request, 'inventory/home.html', context)

@login_required
def IngredientList(request):
    # SQL query to return list of all Ingredient tuples
    ingredients = Ingredient.objects.raw("SELECT * FROM inventory_ingredient")
    # 'data' is used in ingredientList.html to refer to 'ingredients'
    context = {'data': ingredients}
    return render(request, 'inventory/ingredientList.html', context)

@login_required
def MenuItemList(request):
    # SQL query to return list of all MenuItem tuples
    menuItems = MenuItem.objects.raw("SELECT * FROM inventory_menuitem")
    # 'menuItemData' is used in menuItemList.html to refer to 'menuItems'
    context = {'menuItemData': menuItems}
    return render(request, 'inventory/menuItemList.html', context)

@login_required
def OrderList(request):
    # SQL query to return list of all Order tuples
    orders = Order.objects.raw("SELECT * FROM inventory_order")
    # 'orderData' is used in orderList.html to refer to 'orders'
    context = {'orderData': orders}
    return render(request, 'inventory/orderList.html', context)

@login_required
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

class IngredientCreateView(LoginRequiredMixin, CreateView):
    model = Ingredient
    success_url = reverse_lazy('ingredientlist')
    template_name = 'inventory/ingredientCreateForm.html'
    form_class = IngredientCreateForm

class MenuItemCreateView(LoginRequiredMixin, CreateView):
    model = MenuItem
    success_url = reverse_lazy('menuitemlist')
    template_name = 'inventory/menuItemCreateForm.html'
    form_class = MenuItemCreateForm

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    context_object_name = 'orders'
    success_url = reverse_lazy('orderlist')
    template_name = 'inventory/orderCreateForm.html'
    form_class = OrderCreateForm
    
    def post(self, request, *args, **kwargs):
        # Create new Order object, fill fields with input from POST request
        newOrder = Order.objects.create()
        newOrder.item_id = request.POST['item']
        newOrder.time = request.POST['time']
        newOrder.save()
        # Retrieve recipeRequirements corresponding to the MenuItem in the new Order
        recipereqs = RecipeRequirement.objects.raw('''SELECT * FROM inventory_reciperequirement
                                                 WHERE item_id = %s''', [newOrder.item_id])
        # Update Ingredient inventory to reflect ingredients used in new Order
        for item in recipereqs:
            item.ingredient.quantity -= item.quantity
            item.ingredient.save()

        return redirect('orderlist')
        

class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = RecipeRequirement
    template_name = 'inventory/recipeCreateForm.html'
    form_class = RecipeCreateForm
    success_url = reverse_lazy('recipelist')

class IngredientUpdateView(LoginRequiredMixin, UpdateView):
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


class MenuItemUpdateView(LoginRequiredMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemUpdateForm
    template_name = "inventory/menuItemUpdateForm.html"
    success_url = reverse_lazy('menuitemlist')

class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderUpdateForm
    template_name = "inventory/orderUpdateForm.html"
    success_url = reverse_lazy('orderlist')

class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    model = RecipeRequirement
    form_class = RecipeUpdateForm
    template_name = "inventory/recipeUpdateForm.html"
    success_url = reverse_lazy('recipelist')

class IngredientDeleteView(LoginRequiredMixin, DeleteView):
    model = Ingredient
    template_name = "inventory/ingredientDeleteForm.html"
    success_url = reverse_lazy('ingredientlist')

class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = "inventory/orderDeleteForm.html"
    success_url = reverse_lazy('orderlist')

    def post(self, request, *args, **kwargs):
        # Retrieve Order object to be deleted from POST request
        order = self.get_object()
        # Update Ingredients inventory
        # Retrieve recipeRequirements corresponding to the MenuItem in the Order
        recipereqs = RecipeRequirement.objects.raw('''SELECT * FROM inventory_reciperequirement
                                                 WHERE item_id = %s''', [order.item_id])
        # Update Ingredient inventory to reflect restocking ingredients used in Order
        for item in recipereqs:
            item.ingredient.quantity += item.quantity
            item.ingredient.save()

        # Delete order
        order.delete()

        return redirect('orderlist')

class MenuItemDeleteView(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = "inventory/menuItemDeleteForm.html"
    success_url = reverse_lazy("menuitemlist")

class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = RecipeRequirement
    template_name = "inventory/recipeDelete.html"
    success_url = reverse_lazy("recipelist")

def LoginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
    
        # Check if there is user object matching username and password
        user = authenticate(request, username=username, password=password)

        # Check if user exists and is authenticated
        if user is not None:
            # Log user in
            login(request, user)
            # Redirect to home page
            return redirect('home')

    return render(request, 'registration/login.html')

def LogoutView(request):
    logout(request)
    return redirect('home')