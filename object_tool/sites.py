# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AdminSite


__all__ = (
    "CustomObjectToolAdminSite", "CustomObjectToolAdminSiteMixin", "site")


class CustomObjectToolAdminSiteMixin(object):
    """
    You need mix this class to your own admin site if you want to
    add some custom admin object tools to your changelist globally
    """

    def __init__(self, *args, **kwargs):
        super(CustomObjectToolAdminSiteMixin, self).__init__(*args, **kwargs)
        self._object_tools = defaultdict(dict)
        self._global_object_tools = defaultdict(dict)

    def add_object_tool(self, tool, view="", name=None):
        """
        Register an tool to be available globally.
        """
        name = name or tool.__name__
        self._object_tools[view][name] = tool
        self._global_object_tools[view][name] = tool

    def disable_object_tool(self, name, view=""):
        """
        Disable a globally-registered tool. Raise KeyError for invalid names.
        """
        del self._object_tools[view][name]

    def get_object_tool(self, name):
        """
        Explicitly get a registered global tool whether it's enabled or
        not. Raise KeyError for invalid names.
        """
        all_tools = {}
        for tools in self._global_object_tools.values():
            all_tools.update(tools)
        return all_tools[name]

    def get_object_tools(self, view=""):
        """
        Get all the enabled tools as an iterable of (name, func).
        """
        rv = list(self._object_tools[""].items())
        if view:
            rv.extend(self._object_tools[view].items())
        return rv


class CustomObjectToolAdminSite(CustomObjectToolAdminSiteMixin, AdminSite):
    pass


def patch_admin(patch_site=None, patch_modeladmin=None):
    """replace default admin with object tool admin"""
    if patch_site is None:
        patch_site = getattr(settings, "OBJECT_TOOL_PATCHADMINSITE", True)
    if patch_modeladmin is None:
        patch_modeladmin = getattr(
            settings, "OBJECT_TOOL_PATCHMODELADMIN", False)
    if patch_modeladmin:
        patch_site = True

    if patch_site:
        site._registry.update(admin.site._registry)
        setattr(admin.sites, "site", site)
        setattr(admin, "site", site)

    if patch_modeladmin:
        from .admin import CustomObjectToolModelAdmin
        setattr(admin.ModelAdmin, CustomObjectToolModelAdmin)
        setattr(admin.options.ModelAdmin, CustomObjectToolModelAdmin)


site = CustomObjectToolAdminSite()
