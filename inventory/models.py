from django.db import models
from django.db.models.deletion import SET_NULL

# Create your models here.

class Ingredient(models.Model):
    name = models.CharField(primary_key=True, default="New Ingredient", max_length=30)
    cost = models.DecimalField(default=0.0, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(default="g", max_length=10)

class MenuItem(models.Model):
    name = models.CharField(primary_key=True, default="New Menu Item", max_length=30)
    cost = models.DecimalField(default=0.0, decimal_places=2)

class Order(models.Model):
    item = models.ForeignKey(MenuItem, on_delete=SET_NULL, blank=True, null=True)
    time = models.DateTimeField()

class RecipeRequirement(models.Model):
   item = models.ForeignKey(MenuItem, on_delete=SET_NULL, blank=True, null=True)
   ingredient = models.ForeignKey(Ingredient, on_delete=SET_NULL, blank=True, null=True) 
   quantity = models.DecimalField(default=1)
