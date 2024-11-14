import os
import uuid
from django.core.validators import MinValueValidator
from django.db import models
from authentication.models import User


def generate_image_path(instance, filename):
    model_name = instance.__class__.__name__.lower()
    unique_filename = f"{uuid.uuid4().hex}/{instance.name}"
    return os.path.join('images', model_name, unique_filename)


class Restaurant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=100)
    cover_photo = models.ImageField(
        upload_to=generate_image_path,
        null=True,
        blank=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')

    def __str__(self):
        return self.name


class Menu(models.Model):
    name = models.CharField(max_length=255)
    restaurant = models.ForeignKey(Restaurant, related_name="menus", on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class MenuCategory(models.Model):
    name = models.CharField(max_length=255)
    cover_photo = models.ImageField(
        upload_to=generate_image_path,
        null=True,
        blank=True
    )
    menu = models.ForeignKey(Menu, related_name="category", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(
        upload_to=generate_image_path,
        null=True,
        blank=True
    )
    price = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    category = models.ForeignKey(MenuCategory, related_name="dishes", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    dish = models.ForeignKey(Dish, related_name="ingredients", on_delete=models.CASCADE)

    def __str__(self):
        return self.name
