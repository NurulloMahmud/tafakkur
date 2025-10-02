from django.urls import path
from .views import ProductSearchView, CategorySearchView, ProductListCreateView, CategoryListCreateView

urlpatterns = [
    path('products/search/', ProductSearchView.as_view(), name='product-search'),
    path('categories/search/', CategorySearchView.as_view(), name='category-search'),
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
]