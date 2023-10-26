from django.contrib import admin

from .models import (
    Forms, 
    Events, 
    Tickets
)

[admin.site.register(x) for x in (
    Forms, 
    Events, 
    Tickets
)]