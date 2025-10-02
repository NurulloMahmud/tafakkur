# users/documents.py
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import User

@registry.register_document
class UserDocument(Document):
    id = fields.KeywordField()
    email = fields.TextField(analyzer='standard')
    first_name = fields.TextField(analyzer='standard')
    last_name = fields.TextField(analyzer='standard')

    class Index:
        name = 'users'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = User
        fields = []

    def prepare_id(self, instance):
        return str(instance.id)