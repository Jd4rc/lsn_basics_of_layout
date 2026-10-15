from django.contrib import admin
from .models import Category, Product, ContactInfo, Feedback


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'is_published')
    list_filter = ('category', 'is_published')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'views_count')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'email', 'address')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('created_at',)