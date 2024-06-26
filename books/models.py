from django.db import models


class Book(models.Model):
    HARD = 'HARD'
    SOFT = 'SOFT'
    COVER_CHOICES = [
        (HARD, 'Hardcover'),
        (SOFT, 'Softcover'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    cover = models.CharField(max_length=4, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField(default=1)
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.title
