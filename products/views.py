from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from .documents import ProductDocument, CategoryDocument


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductSearchView(APIView):
    pagination_class = StandardPagination

    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return Response({'results': [], 'total': 0}, status=status.HTTP_200_OK)

        s = ProductDocument.search().query(
            'multi_match',
            query=query,
            fields=['title', 'description'],
            fuzziness='AUTO'
        )

        paginator = self.pagination_class()
        results = s.execute()
        paginated_results = paginator.paginate_queryset(results, request)
        serializer = ProductSerializer([Product.objects.get(id=hit.id) for hit in paginated_results], many=True)

        return paginator.get_paginated_response({
            'results': serializer.data,
            'total': results.hits.total.value
        })

class CategorySearchView(APIView):
    pagination_class = StandardPagination

    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return Response({'results': [], 'total': 0}, status=status.HTTP_200_OK)

        s = CategoryDocument.search().query(
            'multi_match',
            query=query,
            fields=['title', 'description'],
            fuzziness='AUTO'
        )

        paginator = self.pagination_class()
        results = s.execute()
        paginated_results = paginator.paginate_queryset(results, request)
        serializer = CategorySerializer([Category.objects.get(id=hit.id) for hit in paginated_results], many=True)

        return paginator.get_paginated_response({
            'results': serializer.data,
            'total': results.hits.total.value
        })


"""
I am leaving the following endpoints simple as i don't know exact requirements and don't have much time
I would implement custom permissions on create, update and delete endpoints if i knew more requirements and have more time
"""
class ProductListCreateView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryListCreateView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)