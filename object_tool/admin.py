# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
from functools import wraps

from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import csrf_protect_m
from django.http import response
from django.utils.text import capfirst
import six

from .sites import CustomObjectToolAdminSiteMixin


class CustomObjectToolModelAdminMixin(object):
    """
    If you want to use custom object tool in your modeladmin,
    you should mix this class to your model admin
    """

    object_tools = []
    change_list_object_tools = []

    @property
    def _base_change_list_template(self):
        opts = self.model._meta
        app_label = opts.app_label
        parent = super(CustomObjectToolModelAdminMixin, self)
        return getattr(parent, "change_list_template", None)\
            or "admin/change_list.html"

    change_list_template = "admin/object_tool/change_list.html"

    def _get_base_object_tools(self, request):
        """
        Return the list of object tools
        """
        object_tools = []

        # Gather object tools from the admin site first
        if isinstance(self.admin_site, CustomObjectToolAdminSiteMixin):
            for (name, func) in self.admin_site.object_tools:
                description = getattr(
                    func, "short_description", name.replace("_", " "))
                object_tools.append((func, name, description))

        # Then gather them from the model admin and all parent classes
        for klass in self.__class__.mro()[::-1]:
            # TODO: filter object tools by view
            class_tools = getattr(klass, "object_tools", []) or []
            object_tools.extend(map(self.get_object_tool, class_tools))

        return self._filter_object_tools_by_permissions(request, object_tools)

    def _filter_object_tools_by_permissions(self, request, object_tools):
        """Filter out any object tools that the user doesn't have access to"""
        filtered_object_tools = []
        for tool in object_tools:
            callable = tool[0]
            if not hasattr(callable, "allowed_permissions"):
                filtered_object_tools.append(tool)
                continue
            permission_checks = (
                getattr(self, "has_%s_permission" % permission)
                for permission in callable.allowed_permissions
            )
            any(
                has_permission(request)
                for has_permission in permission_checks
            ) and filtered_object_tools.append(tool)
        return filtered_object_tools

    def get_object_tools(self, request):
        """
        Return a dictionary mapping the names of all object tools for this
        ModelAdmin to a tuple of (callable, name, description) for each object
        tool.
        """
        tools = self._get_base_object_tools(request)
        # Convert the object_tools into an OrderedDict keyed by name.
        return OrderedDict(
            (name, (func, name, desc))
            for func, name, desc in tools
        )

    def get_object_tool(self, object_tool):
        """
        Return a given object tool from a parameter, which can either be a
        callable, or the name of a method on the ModelAdmin.  Return is a
        tuple of (callable, name, description).
        """
        # If the object tool is a callable, just use it.
        if callable(object_tool):
            func = object_tool
            object_tool = object_tool.__name__

        # Next, look for a method. Grab it off self.__class__ to get an unbound
        # method instead of a bound one; this ensures that the calling
        # conventions are the same for functions and methods.
        elif hasattr(self.__class__, object_tool):
            func = getattr(self.__class__, object_tool)

        # Finally, look for a named method on the admin site
        elif isinstance(self.admin_site, CustomObjectToolAdminSiteMixin):
            try:
                func = self.admin_site.get_object_tool(object_tool)
            except KeyError:
                return None
        
        else:
            return None

        if hasattr(func, "short_description"):
            description = func.short_description
        else:
            description = capfirst(object_tool.replace("_", " "))
        return func, object_tool, description

    def response_object_tool(self, request, obj=None):
        """
        Handle an admin object tool.
        """
        object_tools = self.get_object_tools(request)
        object_tool = object_tools[request.POST["object-tool"]]
        func = object_tool[0]
        rv = func(self, request, obj)
        if isinstance(rv, response.HttpResponseBase):
            return rv
        else:
            return response.HttpResponseRedirect(request.get_full_path())

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        # update context
        object_tools = self.get_object_tools(request)
        extra_context = extra_context or {}
        extra_context.update(
            object_tools=object_tools.values(),
            base_change_list_template=self._base_change_list_template
        )

        rv = super(CustomObjectToolModelAdminMixin, self).changelist_view(
            request, extra_context)

        # handle object tool behaviors
        if request.method == "POST"\
            and "object-tool" in request.POST\
            and request.POST["object-tool"] in object_tools\
            and '_save' not in request.POST:

            rv = self.response_object_tool(request)

        return rv


class CustomObjectToolModelAdmin(CustomObjectToolModelAdminMixin, ModelAdmin):
    pass
