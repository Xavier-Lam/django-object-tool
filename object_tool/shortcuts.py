# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import HttpResponseRedirect


def link_object_tool(url, short_description, **kwargs):
    """
    A short cut for superlink object tool
    
        class DebugAdmin(CustomObjectToolModelAdminMixin, ModelAdmin):
            object_tools = ["forkme"]

            forkme = link_object_tool(
                "https://github.com/Xavier-Lam/django-object-tool", _("fork"))
    """
    def decorated_func(modeladmin, request, obj=None):
        return HttpResponseRedirect(url)

    kwargs["short_description"] = short_description
    for key, value in kwargs.items():
        setattr(decorated_func, key, value)

    return decorated_func