from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0006_documentextraction"),  # adjust this
    ]

    operations = [
        VectorExtension(),
    ]
