from django.contrib import admin
from .models import Category, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'condition')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')