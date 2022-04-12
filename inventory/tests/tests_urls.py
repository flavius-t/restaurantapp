from django.test import SimpleTestCase
from django.urls import reverse, resolve
from inventory.views import home, IngredientList, MenuItemList, OrderList 

class TestUrls(SimpleTestCase):
    def test_home_url_is_resolved(self):
        url = reverse('home')
        self.assertEquals(resolve(url).func, home)

    def test_ingredientlist_url_is_resolved(self):
        url = reverse('ingredientlist')
        self.assertEquals(resolve(url).func, IngredientList)

    def test_menuitemlist_url_is_resolved(self):
        url = reverse('menuitemlist')
        self.assertEquals(resolve(url).func, MenuItemList)

    def test_orderlist_url_is_resolved(self):
        url = reverse('orderlist')
        self.assertEquals(resolve(url).func, OrderList)
