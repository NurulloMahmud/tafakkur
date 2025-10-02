from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Product, Category

@registry.register_document
class ProductDocument(Document):
    id = fields.KeywordField()
    title = fields.TextField(analyzer='standard')
    description = fields.TextField(analyzer='standard')

    class Index:
        name = 'products'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Product
        fields = []

    def prepare_id(self, instance):
        return str(instance.id)

@registry.register_document
class CategoryDocument(Document):
    id = fields.KeywordField()
    title = fields.TextField(analyzer='standard')
    description = fields.TextField(analyzer='standard')

    class Index:
        name = 'categories'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Category
        fields = []

    def prepare_id(self, instance):
        return str(instance.id)
