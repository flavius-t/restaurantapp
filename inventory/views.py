from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from .models import Ingredient, MenuItem, RecipeRequirement, Order
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from .forms import ChangePassword, EditUserForm, IngredientCreateForm, IngredientUpdateForm, MenuItemCreateForm, MenuItemUpdateForm, OrderCreateForm, RecipeCreateForm, RecipeUpdateForm, UserSignUpForm, UserLoginForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from datetime import date
from django.utils.timezone import make_aware
import datetime

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
    
    # Display costs to restock ingredients whose quantity has fallen below 10,
    # where cost is amount needed to raise quantity back to 10
    restockDict = {}
    for item in ingredients:
        if item.quantity < 10:
            restockCost = item.cost * (10 - item.quantity)
            key = item.name
            restockDict[key] = restockCost
    # Calculate total restock cost
    totalCost = 0
    for key in restockDict:
        totalCost += restockDict[key]
    # 'data' is used in ingredientList.html to refer to 'ingredients'
    context = {'data': ingredients, 'restockCosts': restockDict, 'totalCost': totalCost}
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
    orders = Order.objects.all()

    # Calculate total revenue
    totalRevenue = 0
    yearRevenue = 0
    todayRevenue = 0
    monthRevenue = 0
    todayDate = date.today()
    print("Today's Date: " + str(todayDate))
    print(todayDate.day)
    yearStart = todayDate.year
    print(todayDate.year)
    # Retrieve list of all MenuItems related to each Order object
    for order in orders:
        items = order.item.all()
        # Calculate revenue from each MenuItem of each Order
        for menuItem in items:
            # add this item's cost to total revenue
            totalRevenue += menuItem.cost
            # Calculate this year's revenue
            if order.time.year == yearStart:
                # print("Year Match:" + str(order.time.year))
                yearRevenue += menuItem.cost
                # Calculate this month's revenue (i.e. month 2 of this year)
                if order.time.month == todayDate.month:
                    # print("Month Match:" + str(order.time.month))
                    monthRevenue += menuItem.cost
                    print("Order Day:" + str(order.time.day))
                    # Calculate today's revenue--note, uses UTC date-time.
                    if order.time.day == todayDate.day:
                        print("Day Match:" + str(order.time.day))
                        todayRevenue += menuItem.cost
    # 'orderData' is used in orderList.html to refer to 'orders'
    context = {
        'orderData': orders, 
        'total': totalRevenue, 
        'yearTotal': yearRevenue,
        'monthTotal': monthRevenue,
        'todayTotal': todayRevenue,
        }
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
        # retrieve list from manytomany field in POST request, add to new Order object
        items = request.POST.getlist('item')
        for x in items:
            newOrder.item.add(x)
        newOrder.time = request.POST['time']
        newOrder.save()

        for menuItem in newOrder.item.all():
            print(menuItem.name)
            # Retrieve recipeRequirements corresponding to the MenuItem in the new Order
            recipereqs = RecipeRequirement.objects.raw('''SELECT * FROM inventory_reciperequirement
                                                    WHERE item_id = %s''', [menuItem.name])
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
        # Retrieve recipeRequirements corresponding to each MenuItem in the Order
        for menuItem in order.item.all():
            # for this menuItem, retrieve recipe requirements
            recipereqs = RecipeRequirement.objects.raw('''SELECT * FROM inventory_reciperequirement
                                                    WHERE item_id = %s''', [menuItem.name])
            # Update Ingredient inventory to reflect restocking ingredients used in Order
            for item in recipereqs:
                if item is not None:
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

# class UserLoginView(LoginView):
#     template_name = 'registration/login.html'
    # form = UserLoginForm(request.POST)
    
    # if request.method == 'POST':
    #     if form.is_valid:
    #         username = form.get['username']
    #         password = form.get['password']
    
    #         # Check if there is user object matching username and password
    #         user = authenticate(request, username=username, password=password)

    #         # Check if user exists and is authenticated
    #         if user is not None:
    #             # Log user in
    #             login(request, user)
    #             # Redirect to home page
    #             return redirect('home')

    # context = {
    #     "form": form
    # }

    # return render(request, "registration/login.html", context)

def LogoutView(request):
    logout(request)
    return redirect('home')

class PasswordsChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = ChangePassword
    success_url = reverse_lazy('home')
    template_name = "registration/changePassword.html"

class UserEditView(LoginRequiredMixin, UpdateView):
    form_class = EditUserForm
    template_name = "registration/editUser.html"
    success_url = reverse_lazy('home')
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "inventory/orderDetails.html"

def signup(request):
    form = UserSignUpForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        form.save()
        new_user = authenticate(username=username, password=password)
        if new_user is not None:
            login(request, new_user)
            return redirect('home')
    else:
        form = UserSignUpForm()
    
    context = {
        "form": form
    }

    return render(request, "registration/signup.html", context)
