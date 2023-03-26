from django.shortcuts import render
from django.views import View


class Welcome(View):
    """
    The landing page for the site
    """
    def get(self, request):
        return render(request, 'welcome/welcome.html')
