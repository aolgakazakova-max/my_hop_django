from django.contrib import messages
from django.db.models import Avg, Q
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView

from orders.models import OrderItem
from reviews.forms import ReviewForm

from .models import Product, Category


class ProductListView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        qs = (
            Product.objects.filter(is_active=True)
            .select_related('category')
            .annotate(avg_rating=Avg('reviews__rating'))
        )

        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))

        categories = self.request.GET.getlist('category')

        if categories:
            qs = qs.filter(category__slug__in=categories)

        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        if min_price:
            qs = qs.filter(price__gte=min_price)

        if max_price:
            qs = qs.filter(price__lte=max_price)

        sort_map = {
            'new': '-created_at',
            'price_asc': 'price',
            'price_desc': '-price',
            'rating': '-avg_rating',
        }
        sort = self.request.GET.get('sort', 'new')
        return qs.order_by(sort_map.get(sort, '-created_at'))


    def get_context_data(self,  **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['query'] = self.request.GET.get('q', '')
        ctx['min_price'] = self.request.GET.get('min_price', '')
        ctx['max_price'] = self.request.GET.get('max_price', '')
        ctx['selected_categories'] = self.request.GET.getlist('category')
        ctx['current_sort'] = self.request.GET.get('sort', 'new')

        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['querystring'] = params.urlencode()
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product-detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .select_related('category')
            .annotate(avg_rating=Avg('reviews__rating'))
        )



    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['reviews'] = self.object.reviews.select_related('user')

        user = self.request.user

        # Пользователь должен быть авторизован
        can_review = False

        if user.is_authenticated:
            # Проверяем, покупал ли пользователь этот товар
            has_purchased = OrderItem.objects.filter(
                order__user=user,
                product=self.object,
                order__status__in=[
                    'paid',
                    'shipped',
                    'delivered',
                ],
            ).exists()

            # Проверяем, оставлял ли пользователь отзыв
            already_reviewed = self.object.reviews.filter(
                user=user
            ).exists()

            # Оставить отзыв можно только если:
            # 1. товар был куплен
            # 2. отзыва ещё нет
            can_review = has_purchased and not already_reviewed

        ctx['can_review'] = can_review

        if can_review:
            ctx['review_form'] = ReviewForm()
        else:
            ctx['review_form'] = None

        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        user = request.user

        # Пользователь должен быть авторизован
        if not user.is_authenticated:
            messages.error(
                request,
                'Войдите в аккаунт, чтобы оставить отзыв.'
            )
            return redirect(
                'products:detail',
                slug=self.object.slug
            )

        # Проверяем, покупал ли пользователь этот товар
        has_purchased = OrderItem.objects.filter(
            order__user=user,
            product=self.object,
            order__status__in=[
                'paid',
                'shipped',
                'delivered',
            ],
        ).exists()

        if not has_purchased:
            messages.error(
                request,
                'Оставить отзыв можно только после покупки товара.'
            )
            return redirect(
                'products:detail',
                slug=self.object.slug
            )

        # Проверяем, не оставлял ли пользователь отзыв раньше
        already_reviewed = self.object.reviews.filter(
            user=user
        ).exists()

        if already_reviewed:
            messages.error(
                request,
                'Вы уже оставляли отзыв на этот товар.'
            )
            return redirect(
                'products:detail',
                slug=self.object.slug
            )

        # Создаём и проверяем форму
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = self.object
            review.user = user
            review.save()

            messages.success(
                request,
                'Ваш отзыв успешно добавлен.'
            )

            return redirect(
                'products:detail',
                slug=self.object.slug
            )

        # Если форма содержит ошибки,
        # показываем страницу снова вместе с ошибками
        context = self.get_context_data()
        context['review_form'] = form

        return self.render_to_response(context)