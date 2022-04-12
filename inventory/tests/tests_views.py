from django.test import TestCase, Client
from django.urls import reverse
from inventory.models import Order, Ingredient, MenuItem
import json

class TestViews(TestCase):
    def setUp(self):
       self.client = Client()
       self.list_url = reverse('menuitemlist')
       self.order_create_url = reverse('ordercreate')

    def test_ingredientlist_GET(self):
        response = self.client.get(self.list_url)
        self.assertEquals(response.status_code, 302)
    
    def test_ordercreate_POST_adds_new_order(self):
        item = MenuItem.objects.create(
            name='MenuItem1',
            cost=20
        )
        context = {
            'item': item,
            'time': '2022-04-11 01:00:00'
        }
        response = self.client.post(self.order_create_url, context)
        self.assertEquals(response.status_code, 302)

        for order in Order.objects.all():
            self.assertIsNotNone(order)
            self.assertEquals(order.time, '2022-04-11 01:00:00')
            self.assertEquals(order.item, item)
