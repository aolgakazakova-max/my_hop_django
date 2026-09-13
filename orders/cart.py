from decimal import Decimal

from products.models import Product


CART_SESSION_ID = 'cart'


class Cart:
    """Корзина, которая хранится в сессии пользователя."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)

        if cart is None:
            cart = self.session[CART_SESSION_ID] = {}

        self.cart = cart

    def add(self, product, quantity=1, override=False):
        """Добавляет товар в корзину или заменяет его количество."""

        if quantity < 1:
            return

        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
            }

        if override:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def remove(self, product):
        """Удаляет товар из корзины."""

        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """Сообщает Django, что сессию нужно сохранить."""
        self.session.modified = True

    def __iter__(self):
        """Возвращает товары корзины."""

        products = Product.objects.filter(id__in=self.cart.keys())

        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']

            yield item

    def __len__(self):
        """Количество разных товаров в корзине."""
        return len(self.cart)

    def get_total_price(self):
        """Общая стоимость всех товаров в корзине."""

        total_price = Decimal('0.00')

        for item in self.cart.values():
            price = Decimal(item['price'])
            total_price += price * item['quantity']

        return total_price

    def clear(self):
        """Полностью очищает корзину."""

        if CART_SESSION_ID in self.session:
            del self.session[CART_SESSION_ID]

        self.save()

