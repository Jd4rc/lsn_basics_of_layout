from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from catalog.forms import ContactForm, ProductForm
from catalog.models import Category, ContactInfo, Product

PRODUCTS_PER_PAGE = 6


def contacts(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            print(f"Сообщение от {data['name']} ({data['phone']}): {data['message']}")
            messages.success(request, 'Спасибо! Мы свяжемся с тобой в ближайшее время.')
            return redirect('catalog:contacts')
    else:
        form = ContactForm()

    return render(request, 'catalog/contacts.html', {
        'form': form,
        'contact_info': ContactInfo.objects.first(),
    })


def home(request):
    products = Product.objects.filter(is_active=True)

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'catalog/home.html', {
        'products': page_obj,
        'page_obj': page_obj,
    })


class ProductDetailView(DetailView):
    model = Product


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save()
            return redirect('catalog:product_detail', pk=product.pk)
    else:
        form = ProductForm()

    return render(request, 'catalog/product_form.html', {'form': form})


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()
            return redirect('catalog:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'catalog/product_form.html', {'form': form})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        return redirect('catalog:home')

    return render(request, 'catalog/product_confirm_delete.html', {'product': product})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True)

    return render(request, 'catalog/category_detail.html', {
        'category': category,
        'products': products,
    })
