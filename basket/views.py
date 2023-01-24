from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from products.models import Product, SpecialOffer
from datetime import datetime
from django.db.models import Q


class ViewBasket(View):
    """
    A view that shows the contents of the shopping basket.
    """
    def get(self, request):
        basket = request.session.get('basket', {})
        items = []
        special_offers = []
        for id, quantity in basket.items():
            # Check for special offers on each product
            now = datetime.now()
            queries = Q(start_date__lte=now) & Q(end_date__gte=now)
            product = Product.objects.get(pk=id)
            offers = SpecialOffer.objects \
                                 .filter(queries) \
                                 .filter(product=product)
            offer = offers[0] if offers else None
            item = {}
            product = get_object_or_404(Product, pk=int(id))
            item['product'] = product
            item['quantity'] = quantity
            price = offer.reduced_price if offer else product.price
            item['subtotal'] = price * quantity
            items.append(item)

            if offer:
                special_offers.append(offer)

        context = {
            'basket': items,
            'special_offers': special_offers,
        }

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


class RemoveFromBasket(View):
    """ Remove a single product from the basket entirely """
    def post(self, request, product_id):
        redirect_url = request.POST.get('redirect_url')
        basket = request.session.get('basket', {})
        if (product_id in list(basket.keys())):
            basket.pop(product_id)
        request.session['basket'] = basket
        return redirect(redirect_url)


class EmptyBasket(View):
    """
    Removes all items from the basket and returns the user to the main 
    product display page.
    """
    def get(self, request):
        request.session['basket'] = {}
        return redirect('product_display')
