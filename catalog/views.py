# Create your views here.

from django.shortcuts import render, get_object_or_404

from catalog.models import Category


def contacts(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        print(f'Сообщение от {name} ({phone}): {message}')
        return render(request, 'catalog/contacts.html', {'sent': True})

    return render(request, 'catalog/contacts.html')

def home(request):
    return render(request, 'catalog/home.html')

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True)
    return render(request, 'catalog/category_detail.html', {
        'category': category,
        'products': products,
    })
