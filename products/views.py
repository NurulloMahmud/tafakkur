from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from elasticsearch_dsl import Q

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
        query = (request.GET.get('q') or '').strip()
        s = ProductDocument.search()

        if not query:
            # Return empty result set when no query provided
            s = s[0:0]
        else:
            # Prefer exact-ish phrase match, and allow a stricter multi_match fallback without fuzziness
            phrase_q = Q(
                'multi_match',
                query=query,
                fields=['title', 'description'],
                type='phrase'
            )
            strict_q = Q(
                'multi_match',
                query=query,
                fields=['title', 'description'],
                operator='and'  # no fuzziness; requires all terms
            )
            s = s.query('bool', should=[phrase_q, strict_q], minimum_should_match=1)

        paginator = self.pagination_class()
        results = s.execute()
        paginated_results = paginator.paginate_queryset(results, request)

        results_data = [
            {
                'id': hit.id,
                'title': hit.title,
                'description': hit.description,
            } for hit in paginated_results
        ]

        return paginator.get_paginated_response(results_data)


class CategorySearchView(APIView):
    pagination_class = StandardPagination

    def get(self, request):
        query = (request.GET.get('q') or '').strip()
        s = CategoryDocument.search()

        if not query:
            # Return empty result set when no query provided
            s = s[0:0]
        else:
            # Prefer exact-ish phrase match, and allow a stricter multi_match fallback without fuzziness
            phrase_q = Q(
                'multi_match',
                query=query,
                fields=['title', 'description'],
                type='phrase'
            )
            strict_q = Q(
                'multi_match',
                query=query,
                fields=['title', 'description'],
                operator='and'  # no fuzziness; requires all terms
            )
            s = s.query('bool', should=[phrase_q, strict_q], minimum_should_match=1)

        paginator = self.pagination_class()
        results = s.execute()
        paginated_results = paginator.paginate_queryset(results, request)

        results_data = [
            {
                'id': hit.id,
                'title': hit.title,
                'description': hit.description,
            } for hit in paginated_results
        ]

        return paginator.get_paginated_response(results_data)


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