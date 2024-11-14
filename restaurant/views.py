from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from restaurant.models import Restaurant, Menu, MenuCategory, Dish, Ingredient
from restaurant.serializers import RestaurantSerializer, MenuSerializer, MenuCategorySerializer, \
    DetailRestaurantSerializer, AddMenuSerializer, DishSerializer, DishAndIngredientSerializer
from restaurant.permissions import IsOwnerOrReadOnly, IsRestaurantOwnerOrReadOnly, IsMenuOwnerOrReadOnly, \
    IsMenuCategoryOwnerOrReadOnly
from restaurant.filters import MenuCategoryFilter, DishesFilter


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all().order_by('id')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return RestaurantSerializer
        else:
            return DetailRestaurantSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsRestaurantOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return MenuSerializer
        else:
            return AddMenuSerializer


class MenuCategoryViewSet(viewsets.ModelViewSet):
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsMenuOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MenuCategoryFilter

    def perform_create(self, serializer):
        menu = serializer.validated_data['menu']

        if not Menu.objects.filter(id=menu.id, restaurant__user=self.request.user).exists():
            raise PermissionDenied("You do not have permission to perform this action.")

        menu = Menu.objects.get(id=menu.id)
        serializer.save(menu=menu)

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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsMenuCategoryOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DishesFilter

    def perform_create(self, serializer):
        category_obj = serializer.validated_data['category']

        if not MenuCategory.objects.filter(id=category_obj.id, menu__restaurant__user=self.request.user).exists():
            raise PermissionDenied("You do not have permission to perform this action.")

        category_obj = MenuCategory.objects.get(id=category_obj.id)

        serializer.save(category=category_obj)
