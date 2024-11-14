import django_filters
from restaurant.models import MenuCategory, Dish


class MenuCategoryFilter(django_filters.FilterSet):
    menu = django_filters.NumberFilter(field_name='menu__id', lookup_expr='exact', label='Menu Id')

    class Meta:
        model = MenuCategory
        fields = ['menu']

class DishesFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category', lookup_expr='exact', label='Category Id')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Dish Name')

    class Meta:
        model = Dish
        fields = ['category', 'name']






