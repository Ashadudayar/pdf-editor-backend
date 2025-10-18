from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PDFDocumentViewSet

router = DefaultRouter()
router.register(r'documents', PDFDocumentViewSet, basename='pdfdocument')

urlpatterns = [
    path('', include(router.urls)),
]