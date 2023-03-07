from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('welcome.urls')),
    path('products/', include('products.urls')),
    path('basket/', include('basket.urls')),
    path('stock/', include('stock.urls')),
    path('checkout/', include('checkout.urls')),
    path('video_lessons/', include('video_lessons.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom 404 error handler
handler404 = 'strings_attached.views.handler404'
