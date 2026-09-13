from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .cart import Cart
from .forms import OrderForm
from .models import Order, OrderItem


def cart_detail(request):
    cart = Cart(request)

    return render(
        request,
        'cart.html',
        {'cart': cart},
    )


@require_POST
def cart_add(request, product_id):
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
        messages.error(request, 'Количество должно быть не меньше 1.')
        return redirect('products:detail', slug=product.slug)

    current_quantity = cart.cart.get(
        str(product.id),
        {},
    ).get('quantity', 0)

    if current_quantity + quantity > product.stock:
        messages.error(
            request,
            f'Только {product.stock} шт. товара "{product.name}" в наличии.',
        )
        return redirect('products:detail', slug=product.slug)

    cart.add(product, quantity)

    messages.success(
        request,
        f'Товар "{product.name}" добавлен в корзину.',
    )

    return redirect('orders:cart_detail')


@require_POST
def cart_update(request, product_id):
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
            f'Только {product.stock} шт. товара "{product.name}" в наличии.',
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
    cart = Cart(request)

    # Здесь специально НЕ проверяем is_active=True.
    # Даже если товар стал неактивным,
    # пользователь должен иметь возможность удалить его из корзины.
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
    cart = Cart(request)

    if not cart.cart:
        messages.error(
            request,
            'Корзина пуста.'
        )
        return redirect('orders:cart_detail')

    # Проверяем наличие товаров перед оформлением заказа
    for item in cart:
        product = item['product']
        quantity = item['quantity']

        if quantity > product.stock:
            messages.error(
                request,
                f'Недостаточно товара "{product.name}". '
                f'В наличии: {product.stock} шт.'
            )
            return redirect('orders:cart_detail')

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = cart.get_total_price()
            order.save()

            for item in cart:
                product = item['product']
                quantity = item['quantity']

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )

                product.stock -= quantity
                product.save(update_fields=['stock'])

            cart.clear()

            messages.success(
                request,
                f'Заказ №{order.id} успешно оформлен.'
            )

            return redirect('orders:cart_detail')

    else:
        form = OrderForm()

    return render(
        request,
        'checkout.html',
        {
            'cart': cart,
            'form': form,
        },
    )