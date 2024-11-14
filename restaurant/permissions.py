from rest_framework import permissions

from restaurant.models import Restaurant, Menu


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow Admins and owners to edit or delete object.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False


class IsRestaurantOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow Restaurant Owners to edit or delete Menu.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.restaurant.user == request.user


class IsMenuOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow Menu Owners to edit or delete MenuCategories.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.menu.restaurant.user == request.user

class IsMenuCategoryOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow MenuCategory Owners to edit or delete Dishes.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.category.menu.restaurant.user == request.user