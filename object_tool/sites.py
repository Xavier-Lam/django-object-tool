# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
        self._object_tools = {}
        self._global_object_tools = self._object_tools.copy()

    def add_object_tool(self, tool, name=None):
        """
        Register an tool to be available globally.
        """
        name = name or tool.__name__
        self._object_tools[name] = tool
        self._global_object_tools[name] = tool

    def disable_object_tool(self, name):
        """
        Disable a globally-registered tool. Raise KeyError for invalid names.
        """
        del self._object_tools[name]

    def get_object_tool(self, name):
        """
        Explicitly get a registered global tool whether it's enabled or
        not. Raise KeyError for invalid names.
        """
        return self._global_object_tools[name]

    @property
    def object_tools(self):
        """
        Get all the enabled tools as an iterable of (name, func).
        """
        return self._object_tools.items()


class CustomObjectToolAdminSite(CustomObjectToolAdminSiteMixin, AdminSite):
    pass


site = CustomObjectToolAdminSite()
