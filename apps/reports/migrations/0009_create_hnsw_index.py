from django.db import migrations, models
from pgvector.django import HnswIndex


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0008_remove_documentextraction_extracted_contents_and_more')
    ]

    operations = [
        migrations.AddIndex(
            model_name="documentextraction",
            index=HnswIndex(
                name="doc_embedding_hnsw_idx",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
                condition=models.Q(embedding__isnull=False),
            ),
        ),
    ]
