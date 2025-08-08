from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ipo_app.urls')),
    
    # Favicon fallback route
    path('favicon.ico', serve, {'path': 'image/favicon.ico', 'document_root': settings.STATIC_ROOT}),
]

# Serve static and media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
