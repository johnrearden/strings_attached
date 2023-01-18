from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from products.models import Product


class ViewBasket(View):
    """
    A view that shows the contents of the shopping basket.
    """
    def get(self, request):
        basket = request.session.get('basket', {})
        items = []
        for id, quantity in basket.items():
            print(id, quantity)
            item = {}
            product = get_object_or_404(Product, pk=int(id))
            item['product'] = product
            item['quantity'] = quantity
            item['subtotal'] = product.price * quantity
            items.append(item)
        context = {
            'basket': items,
        }
        print(context)

        return render(request, 'basket/basket.html', context)


class AddToBasket(View):
    """
    Add a given quantity of a product to the shopping basket
    """
    def post(self, request, product_id):
        quantity = int(request.POST.get('quantity'))
        redirect_url = request.POST.get('redirect_url')
        basket = request.session.get('basket', {})
        if product_id in list(basket.keys()):
            basket[product_id] += quantity
        else:
            basket[product_id] = quantity

        request.session['basket'] = basket
        return redirect(redirect_url)

