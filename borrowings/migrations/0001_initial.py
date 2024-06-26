# Generated by Django 5.0.6 on 2024-06-26 21:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("books", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Borrowing",
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
                ("borrowing_date", models.DateField(auto_now_add=True)),
                ("expected_returning_date", models.DateField()),
                ("actual_returning_date", models.DateField(blank=True, null=True)),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="books.book"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="borrowing",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("borrowing_date__lt", models.F("expected_returning_date"))
                ),
                name="borrow_date_before_expected_return_date",
            ),
        ),
        migrations.AddConstraint(
            model_name="borrowing",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("actual_returning_date__isnull", True),
                    ("actual_returning_date__gt", models.F("borrowing_date")),
                    _connector="OR",
                ),
                name="actual_return_date_after_borrow_date",
            ),
        ),
    ]
