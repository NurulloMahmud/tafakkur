import time
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Product, Category, ProductCategory
from .documents import ProductDocument, CategoryDocument


class ProductTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Force delete and recreate the specific index
        ProductDocument._index.delete(ignore_unavailable=True)
        ProductDocument._index.create(ignore=[400])

    @classmethod
    def tearDownClass(cls):
        ProductDocument._index.delete(ignore_unavailable=True)
        super().tearDownClass()

    def setUp(self):
        self.client = APIClient()
        # Explicitly delete all documents to clear lingering data
        ProductDocument.search().query("match_all").delete()
        ProductDocument._index.refresh()

        # Create test products
        self.product1 = Product.objects.create(title='Laptop', description='High-end gaming laptop', price=999.99)
        self.product2 = Product.objects.create(title='Phone', description='Smartphone with great camera', price=499.99)
        self.product3 = Product.objects.create(title='Tablet', description='Portable tablet device', price=299.99)

        # Manually index
        for product in Product.objects.all():
            ProductDocument().update(product)
        ProductDocument._index.refresh()
        time.sleep(3)  # Extended for ES to fully process

        # Verify index has exactly 3 docs (debug)
        self.assertEqual(ProductDocument.search().query("match_all").count(), 3)

    def test_product_search(self):
        url = reverse('product-search')
        response = self.client.get(url, {'q': 'high-end gaming'})  # Unique to product1
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)

    def test_product_search_no_query(self):
        url = reverse('product-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['results']), 0)

    def test_product_search_pagination(self):
        url = reverse('product-search')
        response = self.client.get(url, {'q': 'portable tablet', 'page': 1})  # Unique to product3
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(len(data['results']), 1)

    def test_product_list(self):
        url = reverse('product-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 3)

    def test_product_create(self):
        url = reverse('product-list-create')
        data = {'title': 'New Product', 'description': 'Test desc', 'price': 100.00}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 4)

class CategoryTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Force delete and recreate the specific index
        CategoryDocument._index.delete(ignore_unavailable=True)
        CategoryDocument._index.create(ignore=[400])

    @classmethod
    def tearDownClass(cls):
        CategoryDocument._index.delete(ignore_unavailable=True)
        super().tearDownClass()

    def setUp(self):
        self.client = APIClient()
        # Explicitly delete all documents to clear lingering data
        CategoryDocument.search().query("match_all").delete()
        CategoryDocument._index.refresh()

        # Create test categories
        self.category1 = Category.objects.create(title='Electronics', description='Gadgets and devices')
        self.category2 = Category.objects.create(title='Books', description='Fiction and non-fiction')
        self.category3 = Category.objects.create(title='Clothing', description='Apparel and accessories')

        # Manually index
        for category in Category.objects.all():
            CategoryDocument().update(category)
        CategoryDocument._index.refresh()
        time.sleep(3)  # Extended for ES to fully process

        # Verify index has exactly 3 docs (debug)
        self.assertEqual(CategoryDocument.search().query("match_all").count(), 3)

        # Bridge instance
        test_product = Product.objects.create(title='Test Product', price=10.00, description='Test desc')
        ProductCategory.objects.create(product=test_product, category=self.category1)

    def test_category_search(self):
        url = reverse('category-search')
        response = self.client.get(url, {'q': 'gadgets and devices'})  # Unique to category1
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)

    def test_category_search_no_query(self):
        url = reverse('category-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['results']), 0)

    def test_category_search_pagination(self):
        url = reverse('category-search')
        response = self.client.get(url, {'q': 'fiction and non-fiction', 'page': 1})  # Unique to category2
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(len(data['results']), 1)

    def test_category_list(self):
        url = reverse('category-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 3)

    def test_category_create(self):
        url = reverse('category-list-create')
        data = {'title': 'New Category', 'description': 'Test desc'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 4)

    def test_product_category_bridge(self):
        self.assertEqual(ProductCategory.objects.count(), 1)
        product = Product.objects.get(title='Test Product')
        self.assertEqual(product.categories.first().category.title, 'Electronics')