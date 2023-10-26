from django.contrib import admin

from .models import (
    Users,
    Students,
    Porters,
    StudentAffairs
)


for x in (
    Users,
    Students,
    Porters,
    StudentAffairs
):
    admin.site.register(x)
