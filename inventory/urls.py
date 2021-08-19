from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('home/', views.home, name="home"),
    path('ingredients/', views.IngredientList, name='ingredientlist'),
    path('menuitems/', views.MenuItemList, name='menuitemlist'),
    path('orders/', views.OrderList, name='orderlist'),
    path('recipes/', views.RecipeRequirementList, name='recipelist'),
    path('ingredient/create/', views.IngredientCreateView.as_view(), name='ingredientcreate'),
    path('menuitems/create/', views.MenuItemCreateView.as_view(), name='menuitemcreate'),
    path('orders/create/', views.OrderCreateView.as_view(), name='ordercreate'),
    path('recipes/create/', views.RecipeCreateView.as_view(), name='recipecreate'),
    path('ingredient/update/<slug>/', views.IngredientUpdateView.as_view(), name='ingredientupdate'),

]