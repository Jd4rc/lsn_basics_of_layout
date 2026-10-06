from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='home'),
    path('contacts/', views.FeedbackCreateView.as_view(), name='contacts'),
    path('products/new/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('<slug:slug>/', views.CategoryProductListView.as_view(), name='category_detail'),
]
