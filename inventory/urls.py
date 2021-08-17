from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('home/', views.home, name="home"),
    path('ingredients/', views.IngredientList, name='ingredientlist'),
    path('menuitems/', views.MenuItemList, name='menuitemlist'),

]