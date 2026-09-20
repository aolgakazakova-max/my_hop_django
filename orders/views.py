from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .cart import Cart
from .forms import CheckoutForm
from .models import Order
from .services import OutOfStock, create_order


def cart_detail(request):
    """Отображает содержимое корзины."""

    cart = Cart(request)

    return render(
        request,
        'cart.html',
        {
            'cart': cart,
        },
    )


@require_POST
def cart_add(request, product_id):
    """Добавляет товар в корзину."""

    cart = Cart(request)

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        messages.error(
            request,
            'Количество должно быть не меньше 1.',
        )
        return redirect(
            'products:detail',
            slug=product.slug,
        )

    current_quantity = cart.cart.get(
        str(product.id),
        {},
    ).get('quantity', 0)

    if current_quantity + quantity > product.stock:
        messages.error(
            request,
            f'Только {product.stock} шт. товара '
            f'"{product.name}" в наличии.',
        )
        return redirect(
            'products:detail',
            slug=product.slug,
        )

    cart.add(product, quantity)

    messages.success(
        request,
        f'Товар "{product.name}" добавлен в корзину.',
    )

    return redirect('orders:cart_detail')


@require_POST
def cart_update(request, product_id):
    """Изменяет количество товара в корзине."""

    cart = Cart(request)

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        cart.remove(product)

    elif quantity > product.stock:
        messages.error(
            request,
            f'Только {product.stock} шт. товара '
            f'"{product.name}" в наличии.',
        )

    else:
        cart.add(
            product,
            quantity,
            override=True,
        )

    return redirect('orders:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """Удаляет товар из корзины."""

    cart = Cart(request)

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    cart.remove(product)

    messages.info(
        request,
        f'Товар "{product.name}" удалён из корзины.',
    )

    return redirect('orders:cart_detail')


@login_required
def checkout(request):
    """Оформляет заказ из текущей корзины."""

    cart = Cart(request)

    if not cart.cart:
        messages.error(
            request,
            'Корзина пуста.',
        )
        return redirect('orders:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            try:
                order = create_order(
                    user=request.user,
                    cart=cart,
                    data=form.cleaned_data,
                )

            except OutOfStock as error:
                messages.error(
                    request,
                    str(error),
                )
                return redirect('orders:cart_detail')

            except ValueError as error:
                messages.error(
                    request,
                    str(error),
                )
                return redirect('orders:cart_detail')

            cart.clear()

            messages.success(
                request,
                f'Заказ #{order.id} успешно создан.',
            )

            return redirect(
                'orders:order_success',
                order_id=order.id,
            )

    else:
        form = CheckoutForm()

    return render(
        request,
        'checkout.html',
        {
            'cart': cart,
            'form': form,
        },
    )


@login_required
def order_success(request, order_id):
    """Показывает страницу успешно оформленного заказа."""

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    return render(
        request,
        'order_success.html',
        {
            'order': order,
        },
    )