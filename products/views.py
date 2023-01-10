from django.shortcuts import render
from .models import Product
from django.views import View


class ProductDisplay(View):
    """
    Blah
    """
    def get(self, request):
        products = Product.objects.all()
        for product in products:
            print(product.image.name)
        context = {
            'products': products,
        }
        print(context)
        return render(request, 'products/product_display.html', context)
