from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

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


class ProductListView(ListView):
    queryset = Product.objects.filter(is_active=True)
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = PRODUCTS_PER_PAGE

    def paginate_queryset(self, queryset, page_size):
        # Кривой ?page= (abc, 999, 0) даёт ближайшую страницу, а не 404, как в ListView по умолчанию
        paginator = self.get_paginator(queryset, page_size)
        page = paginator.get_page(self.request.GET.get(self.page_kwarg))
        return paginator, page, page.object_list, page.has_other_pages()


class ProductDetailView(DetailView):
    model = Product


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('catalog:home')


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True)

    return render(request, 'catalog/category_detail.html', {
        'category': category,
        'products': products,
    })
