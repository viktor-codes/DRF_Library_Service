# Generated by Django 5.0.6 on 2024-07-02 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("borrowings", "0005_alter_payment_borrowing_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="payment",
            old_name="borrowing_id",
            new_name="borrowing",
        ),
    ]
