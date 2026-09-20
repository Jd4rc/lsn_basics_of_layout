# Create your views here.

from django.shortcuts import render, get_object_or_404

from catalog.models import Category, Product, ContactInfo


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
    latest_products = Product.objects.order_by('-created_at')[:5]
    for product in latest_products:
        print(product)

    return render(request, 'catalog/home.html')

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    return render(request, 'catalog/product_detail.html', {'product': product})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True)


    return render(request, 'catalog/category_detail.html', {
        'category': category,
        'products': products,
    })
