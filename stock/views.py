from django.views.generic.edit import FormView, UpdateView
from .forms import ProductAddForm
from products.models import Product


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
