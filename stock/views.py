from django.views.generic.edit import FormView, UpdateView
from django.shortcuts import render
from django.views import View
from django.db.models import F, Q
from .forms import ProductAddForm
from products.models import Product, SpecialOffer


class ProductAddView(FormView):
    """ A form to allow staff to add a new product """
    template_name = 'stock/product_add_form.html'
    form_class = ProductAddForm
    success_url = '/'


class ProductUpdateView(UpdateView):
    """ A form to allow staff to update an existing product """
    model = Product
    template_name = 'stock/product_update_form.html'
    fields = ['name', 'category', 'description', 'price', 'image',
              'audio_clip', 'stock_level', 'reorder_threshold',
              'product_owner']
    success_url = '/'


class StaffProductList(View):
    """
    Provides a table summarising the complete list of products, which can
    be filtered and sorted by category, price, need for reorder.
    """
    def get(self, request, sort_key):
        manager = Product.objects
        if sort_key == 'all':
            product_list = manager.all()
        elif sort_key == 'price':
            product_list = manager.all().order_by('price')
        elif sort_key == 'stock-low':
            query = Q(stock_level__lte=F('reorder_threshold'))
            product_list = manager.all().filter(query)
        else:
            product_list = manager.all()

        # Check for special offers and adjust price accordingly.
        items = []
        for prod in product_list:
            offers = SpecialOffer.objects.filter(product=prod) \
                .order_by('reduced_price')
            on_offer = True if offers else False
            price = offers[0].reduced_price if on_offer else prod.price
            item = {
                'name': prod.name,
                'id': prod.id,
                'price': price,
                'category': prod.category.name,
                'stock': prod.stock_level,
                'threshold': prod.reorder_threshold,
                'stock_low': prod.stock_level < prod.reorder_threshold,
                'on_special': on_offer,
            }
            items.append(item)
            if sort_key == 'on-special':
                filtered_items = []
                for item in items:
                    if item['on_special'] is True:
                        filtered_items.append(item)
                items = filtered_items
        context = {
            'products': items,
        }
        return render(request, 'stock/staff_product_list.html', context)
