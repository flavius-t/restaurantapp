from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from .models import Ingredient, MenuItem, RecipeRequirement, Order
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from .forms import ChangePassword, EditUserForm, IngredientCreateForm, IngredientUpdateForm, MenuItemCreateForm, MenuItemUpdateForm, OrderCreateForm, RecipeCreateForm, RecipeUpdateForm, UserSignUpForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.db import transaction
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
    # Retrieve list of all Order objects and their related MenuItems, and annotate with total cost
    orders = Order.objects.annotate(total_cost=Sum('item__cost'))

    # Calculate total revenue
    total_revenue = orders.aggregate(Sum('total_cost'))['total_cost__sum'] or 0

    # Calculate revenue for different time periods
    local_tz = timezone.get_current_timezone()
    today_date = timezone.now().astimezone(local_tz).date()
    year_revenue = orders.filter(time__year=today_date.year).aggregate(Sum('item__cost'))['item__cost__sum'] or 0
    month_revenue = orders.filter(time__year=today_date.year, time__month=today_date.month).aggregate(Sum('item__cost'))['item__cost__sum'] or 0
    today_revenue = orders.filter(time__year=today_date.year, time__month=today_date.month, time__day=today_date.day).aggregate(Sum('item__cost'))['item__cost__sum'] or 0

    # 'orderData' is used in orderList.html to refer to 'orders'
    context = {
        'orderData': orders,
        'total': round(total_revenue, 2),
        'yearTotal': round(year_revenue, 2),
        'monthTotal': round(month_revenue, 2),
        'todayTotal': round(today_revenue, 2),
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

class InsufficientInventoryError(Exception):
        pass

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    context_object_name = 'orders'
    success_url = reverse_lazy('orderlist')
    template_name = 'inventory/orderCreateForm.html'
    form_class = OrderCreateForm

    def __create_new_order(self, items: list[MenuItem], aware_time: datetime):
        """
        Helper function to populate new Order object with MenuItem objects from POST request.

        Args:
            `items` (list): List of MenuItem objects to add to Order.
            `time` (datetime): timezone-aware datetime object representing time of Order.
        """
        with transaction.atomic():
            order = Order.objects.create()
            for x in items:
                order.item.add(x)
            order.time = aware_time
            order.save()

    def __get_tz_aware_time(self, request: HttpRequest) -> datetime:
        """
        Helper function to retrieve timezone-aware datetime object from POST request.

        Args:
            `request` (HttpRequest): POST request object from OrderCreateView.

        Returns:
            `datetime`: timezone-aware datetime object representing time of Order.
        """
        # request passed as string, needs to be formatted and made timezone-aware
        strtime = request.POST.get('time')
        if not strtime:
            messages.error(request, "Failed to create new Order: Ensure time has been set.")
            return None

        cleaned_time = strtime.replace('T', ' ', 1)

        try:
            tz_str = request.session.get('django_timezone')
            tz = pytz.timezone(tz_str)
            newdate = datetime.strptime(cleaned_time, "%Y-%m-%d %H:%M")
            now_aware = timezone.make_aware(newdate, timezone=tz)
        except pytz.exceptions.UnknownTimeZoneError:
            messages.error(request, "Failed to create new Order: Unknown timezone. Ensure timezone has been set.")
            return None
        except ValueError:
            messages.error(request, "Failed to create new Order: Invalid time format.")
            return None

        return now_aware
    
    def __update_inventory(self, recipe_items: list[MenuItem]) -> None:
        """
        Helper function to update inventory quantities after new Order is created.

        Args:
            `order` (Order): Order object that was just created.
        """
        # Update quantity of each Ingredient related to each MenuItem; rollback changes if insufficient inventory
        with transaction.atomic():
            for menu_item in recipe_items:
                recipe_reqs = RecipeRequirement.objects.filter(item=menu_item)
                for req in recipe_reqs:
                    ingredient = req.ingredient
                    if ingredient.quantity < req.quantity:
                        raise InsufficientInventoryError(f"Insufficient inventory for ingredient '{ingredient}'.")
                    ingredient.quantity -= req.quantity
                    ingredient.save()

    def __get_menu_items(self, request: HttpRequest) -> list[MenuItem]:
        """
        Helper function to retrieve list of MenuItem objects from POST request.

        Args:
            request (HttpRequest): POST request object from OrderCreateView.

        Returns:
            list: List of MenuItem objects corresponding to MenuItems in POST request.
        """
        items = request.POST.getlist('item')
        menuItems = []
        for item in items:
            try:
                menuItem = MenuItem.objects.get(name=item)
                menuItems.append(menuItem)
            except MenuItem.DoesNotExist:
                messages.error(request, "Failed to create new Order: Invalid MenuItem.")
                return None
        return menuItems
    
    def post(self, request, *args, **kwargs):
        """
        Override POST request handling to allow custom handling of new Order creation.
        """
        # Create new Order object, fill fields with input from POST request
        aware_time = self.__get_tz_aware_time(request)
        menu_items = self.__get_menu_items(request)
        if not (aware_time and menu_items):
            return redirect('orderlist')

        try:
            self.__update_inventory(menu_items)
        except InsufficientInventoryError as e:
            messages.error(request, f"Failed to create new Order due to insufficient inventory: {e}")
            return redirect('orderlist')

        self.__create_new_order(menu_items, aware_time)

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
