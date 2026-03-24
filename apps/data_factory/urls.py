from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataFactoryViewSet
from .excel_filler_view import analyze_excel_template, fill_excel_data, preview_filled_data

router = DefaultRouter()
router.register(r'', DataFactoryViewSet, basename='data-factory')

urlpatterns = [
    path('', include(router.urls)),
    path('excel-filler/analyze/', analyze_excel_template, name='excel-filler-analyze'),
    path('excel-filler/fill/', fill_excel_data, name='excel-filler-fill'),
    path('excel-filler/preview/', preview_filled_data, name='excel-filler-preview'),
]
