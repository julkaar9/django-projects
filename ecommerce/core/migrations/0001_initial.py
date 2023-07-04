# Generated by Django 4.1 on 2023-05-16 19:35

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField()),
                ("description", models.TextField()),
                (
                    "image",
                    models.ImageField(
                        default=True,
                        null=True,
                        upload_to=core.models.category_image_path,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "sub_category",
                    models.ManyToManyField(
                        blank=True,
                        related_name="parent_categories",
                        related_query_name="parent_category",
                        to="core.category",
                    ),
                ),
            ],
        ),
    ]