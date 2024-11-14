from django.db import transaction
from rest_framework import serializers

from restaurant.models import Restaurant, Menu, MenuCategory, Dish, Ingredient


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'name')


class DetailRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'address', 'phone_number', 'cover_photo')


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'name', 'restaurant')


class AddMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'name', 'restaurant')

    def validate_restaurant(self, value):
        user = self.context.get('request').user

        if not user.restaurants.filter(id=value.id).exists():
            raise serializers.ValidationError("You can only add a menu to your own restaurant.")
        return value


class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ('id', 'name', 'cover_photo', 'menu')

    def validate(self, attrs):
        user = self.context.get('request').user
        menu = attrs.get('menu')
        if menu:
            menu = Menu.objects.select_related('restaurant__user').get(id=menu.id)
            if menu.restaurant.user != user:
                raise serializers.ValidationError("You can only add a menu category to your own menu.")
        return attrs


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name')


class DishSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Dish
        fields = ('id', 'name', 'price', 'photo', 'category', 'ingredients')

    def validate(self, attrs):
        user = self.context.get('request').user
        category_attr = attrs.get('category')

        if category_attr:
            category = MenuCategory.objects.select_related('menu__restaurant__user').get(id=category_attr.id)

            if category.menu.restaurant.user != user:
                raise serializers.ValidationError("You can only add a dish to your own menu category.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        dish = Dish.objects.create(**validated_data)

        ingredients = [Ingredient(dish=dish, **ingredient_data) for ingredient_data in ingredients_data]
        Ingredient.objects.bulk_create(ingredients)

        return dish

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])

        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.category = validated_data.get('category', instance.category)
        instance.save()

        existing_ingredient_ids = set(Ingredient.objects.filter(dish_id=instance.id).values_list('id', flat=True))
        incoming_ingredient_ids = set()

        ingredients_to_create = []
        ingredient_to_update = []

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')

            if ingredient_id:
                ingredient_instance = Ingredient.objects.get(id=ingredient_id)
                if ingredient_instance:
                    ingredient_instance.name = ingredient_data.get('name', ingredient_instance.name)
                    ingredient_to_update.append(ingredient_instance)
                    incoming_ingredient_ids.add(ingredient_instance.id)
                else:
                    continue
            else:
                ingredients_to_create.append(Ingredient(dish=instance, **ingredient_data))

        Ingredient.objects.bulk_update(ingredient_to_update, ['name'])

        Ingredient.objects.bulk_create(ingredients_to_create)

        ingredient_to_delete = existing_ingredient_ids - incoming_ingredient_ids

        if ingredient_to_delete:
            Ingredient.objects.filter(id__in=ingredient_to_delete).delete()

        return instance


class DishAndIngredientSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Dish
        fields = ('id', 'name', 'price', 'photo', 'category', 'ingredients')
