from django.shortcuts import render, get_object_or_404
from .models import Product, ProductAssociation
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


class ProductDetail(View):
    """
    Provides all available detail about a single product, and a list
    of the products associated with that product, ordered by weight
    """
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        print(product)
        associated_products = ProductAssociation.objects.filter(
            base_product=product
            ).order_by('-weight')
        p_list = [ap.associated_product for ap in associated_products]
        context = {
            'product': product,
            'associated_products': p_list,
        }
        print(context)
        return render(request, 'products/product_detail.html', context)

