from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/media/', include('media.urls')),
    path('api/albums/', include('albums.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/terms/', include('taxonomy.urls')),
    path('api/social/', include('social.urls')),
    path('api/moderation/', include('moderation.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/memberships/', include('memberships.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/gourl/', include('integrations.gourl.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
