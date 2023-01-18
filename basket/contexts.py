from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product


def basket_contents(request):
    """
    Provides a context processor that all parts of the site can access in order
    to determine the current contents of the basket and the total cost of same.
    """
    basket_items = []
    subtotal = 0
    product_count = 0
    basket = request.session.get('basket', {})
    order_includes_instrument = False

    for id, quantity in basket.items():
        product = get_object_or_404(Product, pk=id)
        subtotal += quantity * product.price
        product_count += quantity
        if product.category.name == 'Instrument':
            order_includes_instrument = True
        basket_items.append({
            'id': id,
            'quantity': quantity,
            'product': product,
        })

    if order_includes_instrument:
        delivery = 0
    else:
        delivery = settings.DEFAULT_DELIVERY_CHARGE

    total = subtotal + delivery

    context = {
        'basket_items': basket_items,
        'subtotal': subtotal,
        'product_count': product_count,
        'delivery': delivery,
        'total': total,
    }

    return context
