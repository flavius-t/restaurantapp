from unicodedata import name
from django.test import TestCase, Client
from django.urls import reverse
from inventory.models import Order, Ingredient, MenuItem
from django.contrib.auth.models import User

from django.utils import timezone
import datetime
import pytz
from decimal import Decimal

class TestMenuItemListView(TestCase):
    def setUp(self):
       self.client = Client()
       self.list_url = reverse('menuitemlist')
       self.order_create_url = reverse('ordercreate')

    def test_ingredientlist_GET(self):
        response = self.client.get(self.list_url)
        self.assertEquals(response.status_code, 302)

class TestOrderCreateView(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        self.client = Client()
        self.order_create_url = reverse('ordercreate')
        self.menu_item_1 = MenuItem.objects.create(
            name='menu-item-1',
            cost=1.99
        )
    
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('ordercreate'))
        self.assertRedirects(response, '/login/?next=/orders/create/')
    
    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('ordercreate'))

        # Check user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that logged in user response "success"
        self.assertEqual(response.status_code, 200)
        # Check correct template used
        self.assertTemplateUsed(response, 'inventory/orderCreateForm.html')

    def test_tz_make_aware(self):
        tz_name = 'US/Pacific'
        self.assertEqual(
            timezone.make_aware(datetime.datetime.now(), timezone=pytz.timezone(tz_name)),
            datetime.datetime.now(tz=pytz.timezone(tz_name))
       )

    def test_POST_adds_new_order(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        tz_name = 'US/Pacific'
        aware_date = timezone.make_aware(datetime.datetime.now(), timezone=pytz.timezone(tz_name))

        self.client.session['django_timezone'] = tz_name
        self.client.session.save()
        
        response = self.client.post(self.order_create_url, {
            'item': self.menu_item_1,
            'time': aware_date
        })
        self.assertEquals(response.status_code, 302)
        print(response.context)

class TestIngredientCreateView(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        self.client = Client()
        self.ingredient_create_url = reverse('ingredientcreate')

    def test_POST_adds_new_ingredient(self):
        ing_name = 'ingredient1'
        ing_cost = 1.99
        ing_quant = 10
        ing_unit = 'g'

        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.post(self.ingredient_create_url, {
        'name': ing_name,
        'cost': ing_cost,
        'quantity': ing_quant,
        'unit': ing_unit
        })
        # check for redirect after POST
        self.assertEquals(response.status_code, 302)
 
        new_ingredient = Ingredient.objects.get(name='ingredient1')
        # check new Ingredient object created
        self.assertIsNotNone(new_ingredient)
        # check proper attributes set
        self.assertEquals(new_ingredient.name, ing_name)
        self.assertAlmostEquals(new_ingredient.cost, Decimal(ing_cost), 2)
        self.assertEquals(new_ingredient.quantity, ing_quant)
        self.assertEquals(new_ingredient.unit, ing_unit)
