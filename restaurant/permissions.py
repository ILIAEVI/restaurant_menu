from django.db.models import Q
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        """
        Custom Permission to only allow Owners to edit or delete object.
        to use this permission class, please write in view query_string.
        for example: query_string = 'restaurant__user_id'
        """
        try:
            query_string = view.query_string
        except AttributeError:
            raise AttributeError('For this permission class, you need to provide query_string in view, Check Implementation')

        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.__class__.objects.filter(Q(id=obj.id) & Q(**{query_string: request.user.id})).exists():
            return True
