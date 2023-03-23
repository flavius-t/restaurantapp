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
from django.contrib import messages
from datetime import date
from django.utils import timezone
from datetime import datetime
import pytz
import logging

_logger = logging.getLogger(__name__)

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
    yearStart = todayDate.year
    # Retrieve list of all MenuItems related to each Order object
    for order in orders:
        print(order.time)
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
                    # Calculate today's revenue--note, uses UTC date-time.
                    if order.time.day == todayDate.day:
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
        """
        Override POST method handling fro this view to allow custom handling of new Order creation.
        """
        # request is passing date as string, need to convert to timezone aware datetime object
        strtime = request.POST['time']
        cleaned_time = strtime.replace('T', ' ', 1)
        try:
            tz_str = request.session.get('django_timezone')
            tz = pytz.timezone(tz_str)
            newdate = datetime.strptime(cleaned_time, "%Y-%m-%d %H:%M")
            now_aware = timezone.make_aware(newdate, timezone=tz)
        except pytz.exceptions.UnknownTimeZoneError:
            _logger.error("Failed to create new Order: Unknown timezone: %s. Ensure timezone has been set.", tz_str)
            messages.error(request, "Failed to create new Order: Ensure timezone has been set.")
            return redirect('orderlist')
            

        # retrieve list from manytomany field in POST request, add to new Order object
        items = request.POST.getlist('item')

        # Create new Order object, fill fields with input from POST request
        newOrder = Order.objects.create()

        for x in items:
            newOrder.item.add(x)
        newOrder.time = now_aware
        newOrder.save()

        for menuItem in newOrder.item.all():
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

# Prepare a map of common locations to timezone choices
common_timezones = {
    'London': 'Europe/London',
    'Paris': 'Europe/Paris',
    'New York': 'America/New_York',
    'San Francisco': 'US/Pacific',
}

def set_timezone(request):
    if request.method == 'POST':
        try:
            # set session timezone, for use by TimezoneMiddleWare
            request.session['django_timezone'] = request.POST['timezone']
        except:
            print("TZ not found")
        return redirect('/')
    else:
        return render(request, 'inventory/set_timezone.html', {'timezones': common_timezones})
