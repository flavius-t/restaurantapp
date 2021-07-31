from django.db import models

# Create your models here.

class Ingredient(models.Model):
    name = models.CharField(primary_key=True, default="New Ingredient", max_length=30)
    cost = models.DecimalField(default=0.0, decimal_places=2)
    quantity = models.IntegerField(default=0)