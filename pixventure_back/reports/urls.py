from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportReasonViewSet, ReportViewSet

router = DefaultRouter()
router.register('reasons', ReportReasonViewSet, basename='report-reason')
router.register('', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
