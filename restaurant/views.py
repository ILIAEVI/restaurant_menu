from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from restaurant.models import Restaurant, Menu, MenuCategory, Dish, Ingredient
from restaurant.serializers import RestaurantSerializer, MenuSerializer, MenuCategorySerializer, \
    DetailRestaurantSerializer, AddMenuSerializer, DishSerializer, DishAndIngredientSerializer, IngredientSerializer
from restaurant.permissions import IsOwnerOrReadOnly
from restaurant.filters import MenuCategoryFilter, DishesFilter


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all().order_by('id')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    query_string = 'user__id'

    def get_serializer_class(self):
        if self.action == 'list':
            return RestaurantSerializer
        else:
            return DetailRestaurantSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    query_string = 'restaurant__user_id'

    def get_serializer_class(self):
        if self.action == 'list':
            return MenuSerializer
        else:
            return AddMenuSerializer


class MenuCategoryViewSet(viewsets.ModelViewSet):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MenuCategoryFilter
    query_string = 'menu__restaurant__user_id'

    @action(
        methods=['get'],
        detail=True,
        permission_classes=[permissions.AllowAny],
        url_path='get-dishes',
        url_name='get-dishes',
        serializer_class=DishAndIngredientSerializer,
    )
    def get_dishes_by_category(self, request, pk=None):
        """
        Action which returns filtered dishes by Category
        """
        menu_category = self.get_object()
        dishes = Dish.objects.filter(category=menu_category)

        serializer = DishAndIngredientSerializer(dishes, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DishesFilter
    query_string = 'category__menu__restaurant__user_id'