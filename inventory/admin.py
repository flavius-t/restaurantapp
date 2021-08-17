from django.contrib import admin

from .models import Ingredient, MenuItem, Order, RecipeRequirement

# Register your models here.
admin.site.register(Ingredient)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(RecipeRequirement)