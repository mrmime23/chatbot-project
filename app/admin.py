from django.contrib import admin
from .models import Group, Intent, Pattern, Response
# Register your models here.
admin.site.register(Group)
admin.site.register(Intent)
admin.site.register(Pattern)
admin.site.register(Response)