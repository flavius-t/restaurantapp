from django.db import models
from django.db.models.deletion import SET_NULL
from django.urls import reverse

# Create your models here.

class Ingredient(models.Model):
    name = models.CharField(primary_key=True, default="New Ingredient", max_length=30)
    cost = models.DecimalField(default=0.0, decimal_places=2, max_digits=5)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(default="g", max_length=10)
    slug = models.SlugField(null=False, unique=True)

    def get_absolute_url(self):
        return reverse('ingredientupdate', kwargs={'slug': self.slug})

class MenuItem(models.Model):
    name = models.CharField(primary_key=True, default="New Menu Item", max_length=30)
    cost = models.DecimalField(default=0.0, decimal_places=2, max_digits=5)

class Order(models.Model):
    item = models.ForeignKey(MenuItem, on_delete=SET_NULL, blank=True, null=True)
    time = models.DateTimeField()

class RecipeRequirement(models.Model):
   item = models.ForeignKey(MenuItem, on_delete=SET_NULL, blank=True, null=True)
   ingredient = models.ForeignKey(Ingredient, on_delete=SET_NULL, blank=True, null=True) 
   quantity = models.DecimalField(default=1, decimal_places=2, max_digits=5)

   def __str__(self):
       return self.item + " " + self.ingredient + " " + self.quantity