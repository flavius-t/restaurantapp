from django.urls import path

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
    path('ingredient/update/<pk>/', views.IngredientUpdateView.as_view(), name='ingredientupdate'),
    path('menuitems/update/<pk>/', views.MenuItemUpdateView.as_view(), name='menuitemupdate'),
    path('orders/update/<pk>/', views.OrderUpdateView.as_view(), name='orderupdate'),
    path('recipes/update/<pk>/', views.RecipeUpdateView.as_view(), name='recipeupdate'),
    path('ingredient/delete/<pk>/', views.IngredientDeleteView.as_view(), name='ingredientdelete'),
    path('order/delete/<pk>/', views.OrderDeleteView.as_view(), name='orderdelete'),
    path('menuitems/delete/<pk>/', views.MenuItemDeleteView.as_view(), name='menuitemdelete'),
]