from django.core.management.base import BaseCommand
from products.documents import ProductDocument, CategoryDocument
from products.models import Product, Category

class Command(BaseCommand):
    help = "Create Elasticsearch indices for Product and Category and index existing DB rows."

    def handle(self, *args, **options):
        # Create indices if missing
        for doc in (ProductDocument, CategoryDocument):
            index = doc._index
            if not index.exists():
                self.stdout.write(self.style.WARNING(f"Creating index: {index._name}"))
                index.create(ignore=400)

        # Index existing DB data
        # Product
        self.stdout.write("Indexing Products...")
        for obj in Product.objects.all():
            ProductDocument().update(obj)
        ProductDocument._index.refresh()

        # Category
        self.stdout.write("Indexing Categories...")
        for obj in Category.objects.all():
            CategoryDocument().update(obj)
        CategoryDocument._index.refresh()

        self.stdout.write(self.style.SUCCESS("Elasticsearch indices bootstrapped and data indexed."))