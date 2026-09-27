from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView

from catalog.forms import ContactForm, ProductForm
from catalog.models import Category, ContactInfo, Product

PRODUCTS_PER_PAGE = 6


class ContactFormView(SuccessMessageMixin, FormView):
    form_class = ContactForm
    template_name = 'catalog/contacts.html'
    success_url = reverse_lazy('catalog:contacts')
    success_message = 'Спасибо! Мы свяжемся с тобой в ближайшее время.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_info'] = ContactInfo.objects.first()
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        print(f"Сообщение от {data['name']} ({data['phone']}): {data['message']}")
        return super().form_valid(form)


class NearestPageMixin:
    """Пагинация без 404: ставится левее ListView."""

    def paginate_queryset(self, queryset, page_size):
        # Кривой ?page= (abc, 999, 0) даёт ближайшую страницу, а не 404, как в ListView по умолчанию
        paginator = self.get_paginator(queryset, page_size)
        page = paginator.get_page(self.request.GET.get(self.page_kwarg))
        return paginator, page, page.object_list, page.has_other_pages()


class ProductListView(NearestPageMixin, ListView):
    queryset = Product.objects.filter(is_active=True)
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = PRODUCTS_PER_PAGE


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


class CategoryProductListView(NearestPageMixin, ListView):
    template_name = 'catalog/category_detail.html'
    context_object_name = 'products'
    paginate_by = PRODUCTS_PER_PAGE

    def get_queryset(self):
        # 404 на несуществующий слаг, иначе <slug:slug>/ отдаст пустую «категорию» с кодом 200
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return self.category.products.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
