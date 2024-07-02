from django.contrib import admin

from .models import Borrowing, Payment

admin.site.register(Borrowing)
admin.site.register(Payment)
