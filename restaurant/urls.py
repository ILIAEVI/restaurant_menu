from django.urls import path, include
from rest_framework.routers import DefaultRouter
from restaurant import views


router = DefaultRouter()
router.register(r'restaurants', views.RestaurantViewSet)
router.register(r'menus', views.MenuViewSet)
router.register(r'menu-categories', views.MenuCategoryViewSet)
router.register(r'dishes', views.DishViewSet)

urlpatterns = [
    path('', include(router.urls)),
]