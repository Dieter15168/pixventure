# integrations/gourl/urls.py

from django.urls import path
from integrations.gourl import views

urlpatterns = [
    path('gourl_callback/', views.callback, name='gourl_callback'),
]
