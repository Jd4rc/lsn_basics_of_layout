from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from catalog.forms import ProductForm
from catalog.models import Category, ContactInfo, Product

PRODUCTS_PER_PAGE = 6


def contacts(request):
    contact_info = ContactInfo.objects.first()

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        print(f'Сообщение от {name} ({phone}): {message}')
        return render(request, 'catalog/contacts.html', {'sent': True, 'contact_info': contact_info})

    return render(request, 'catalog/contacts.html', {'contact_info': contact_info})


def home(request):
    products = Product.objects.filter(is_active=True)

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'catalog/home.html', {
        'products': page_obj,
        'page_obj': page_obj,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    return render(request, 'catalog/product_detail.html', {'product': product})


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save()
            return redirect('catalog:product_detail', pk=product.pk)
    else:
        form = ProductForm()

    return render(request, 'catalog/product_form.html', {'form': form})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True)

    return render(request, 'catalog/category_detail.html', {
        'category': category,
        'products': products,
    })
