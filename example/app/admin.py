# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from object_tool import CustomObjectToolModelAdminMixin, link_object_tool

from .models import User


class UserAdmin(CustomObjectToolModelAdminMixin, admin.ModelAdmin):
    object_tools = ("make_handsome",)
    changelist_object_tools = ("forkme", )

    list_display = ("name", "handsome")

    forkme = link_object_tool(
        "https://github.com/Xavier-Lam/django-object-tool",
        "Fork me on github")

    def make_handsome(self, request, obj=None):
        if obj:
            obj.handsome = True
            obj.save()
        else:
            self.get_queryset(request).all().update(handsome=True)

admin.site.register(User, UserAdmin)
