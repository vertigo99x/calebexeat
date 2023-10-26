from django.contrib import admin

# Register your models here.
from .models import (
    Colleges,
    Departments,
    Hostels,
)

[admin.site.register(x) for x in (
    Colleges,
    Departments,
    Hostels,
)]