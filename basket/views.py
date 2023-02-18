from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
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
        product = Product.objects.get(pk=product_id)
        msg = f'Added {quantity} x {product.name} to your basket!'
        messages.success(request, msg)
        return redirect(redirect_url)


class RemoveFromBasket(View):
    """ Remove a single product from the basket entirely """
    def post(self, request, product_id):
        redirect_url = request.POST.get('redirect_url')
        basket = request.session.get('basket', {})
        if (product_id in list(basket.keys())):
            basket.pop(product_id)
        request.session['basket'] = basket

        # Notify the user with a success message
        product = Product.objects.get(pk=product_id)
        msg = f'{product.name} removed from basket.'
        messages.success(request, msg)

        return redirect(redirect_url)


class ReplaceItemQuantity(View):
    """ Delete the current item quantity and replace it with the new quantity
        in the POST request"""
    def post(self, request, product_id):
        redirect_url = request.POST.get('redirect_url')
        basket = request.session.get('basket', {})
        new_quantity = int(request.POST.get('quantity'))
        if (product_id in list(basket.keys())):
            basket[product_id] = new_quantity
        request.session['basket'] = basket

        # Notify the user with a success message
        product = Product.objects.get(pk=product_id)
        msg = f'Your basket now has {new_quantity} x {product.name}'
        messages.success(request, msg)

        return redirect(redirect_url)


class EmptyBasket(View):
    """
    Removes all items from the basket and returns the user to the main
    product display page.
    """
    def post(self, request):
        request.session['basket'] = {}
        messages.success(request, 'All items removed from basket.')
        return redirect('product_display')
