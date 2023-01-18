from django.shortcuts import render, redirect
from django.views import View


class ViewBasket(View):
    """
    A view that shows the contents of the shopping basket.
    """
    def get(self, request):
        return render(request, 'basket/basket.html')


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

