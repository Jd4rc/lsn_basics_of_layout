from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from catalog.emails import send_views_milestone_email
from catalog.forms import FeedbackForm, ProductForm
from catalog.models import Category, ContactInfo, Feedback, Product
from catalog.services import get_published_products_by_category

PRODUCTS_PER_PAGE = 6
VIEWS_MILESTONE = 100


class FeedbackCreateView(SuccessMessageMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'catalog/contacts.html'
    success_url = reverse_lazy('catalog:contacts')
    success_message = 'Спасибо! Мы свяжемся с тобой в ближайшее время.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_info'] = ContactInfo.objects.first()
        return context


class NearestPageMixin:
    """Пагинация без 404: ставится левее ListView."""

    def paginate_queryset(self, queryset, page_size):
        # Кривой ?page= (abc, 999, 0) даёт ближайшую страницу, а не 404, как в ListView по умолчанию
        paginator = self.get_paginator(queryset, page_size)
        page = paginator.get_page(self.request.GET.get(self.page_kwarg))
        return paginator, page, page.object_list, page.has_other_pages()


class OwnerOrPermissionMixin:
    """Объект доступен его владельцу или пользователю с правом moderator_permission.

    Ставится левее UpdateView / DeleteView. Остальным — 403.
    """

    moderator_permission = None

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        # owner_id, а не owner: сравнение без лишнего запроса за пользователем
        if obj.owner_id != user.pk and not user.has_perm(self.moderator_permission):
            raise PermissionDenied
        return obj


class ProductListView(NearestPageMixin, ListView):
    queryset = Product.objects.filter(is_published=True)
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = PRODUCTS_PER_PAGE


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product

    def get_object(self, queryset=None):
        product = super().get_object(queryset)
        # update() с F(), а не save(): save() сдвинул бы updated_at (auto_now) при каждом просмотре.
        # UPDATE держит строку до конца транзакции, поэтому каждый запрос читает своё новое
        # значение: при одновременных открытиях VIEWS_MILESTONE увидит ровно один
        with transaction.atomic():
            Product.objects.filter(pk=product.pk).update(views_count=F('views_count') + 1)
            product.refresh_from_db(fields=['views_count'])
        if product.views_count == VIEWS_MILESTONE:
            send_views_milestone_email(product, self.request.build_absolute_uri(product.get_absolute_url()))
        return product


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm

    def form_valid(self, form):
        # Поля owner в форме нет: владелец — тот, кто создаёт товар
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, OwnerOrPermissionMixin, UpdateView):
    model = Product
    form_class = ProductForm
    moderator_permission = 'catalog.change_product'


class ProductDeleteView(LoginRequiredMixin, OwnerOrPermissionMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('catalog:home')
    moderator_permission = 'catalog.delete_product'


class ProductUnpublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Снять товар с публикации. Только POST: действие меняет данные."""

    permission_required = 'catalog.can_unpublish_product'

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.is_published = False
        product.save()
        messages.success(request, f'Товар «{product.name}» снят с публикации.')
        return redirect(product)


class CategoryProductListView(NearestPageMixin, ListView):
    template_name = 'catalog/category_detail.html'
    context_object_name = 'products'
    paginate_by = PRODUCTS_PER_PAGE

    def get_queryset(self):
        # 404 на несуществующий слаг, иначе <slug:slug>/ отдаст пустую «категорию» с кодом 200
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return get_published_products_by_category(self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
