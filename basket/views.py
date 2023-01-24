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
        for id, quantity in basket.items():
            item = {}
            product = get_object_or_404(Product, pk=int(id))
            item['product'] = product
            item['quantity'] = quantity
            item['subtotal'] = product.price * quantity
            items.append(item)

            # Check for special offers on each product
            now = datetime.now()
            queries = Q(start_date__lte=now) & Q(end_date__gte=now)
            print(f'Queries on special offers : {queries}')
            special_offers = SpecialOffer.objects.filter(queries)
            # special_offers = SpecialOffer.objects.all()

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


class EmptyBasket(View):
    """
    Removes all items from the basket and returns the user to the main 
    product display page.
    """
    def get(self, request):
        request.session['basket'] = {}
        return redirect('product_display')
