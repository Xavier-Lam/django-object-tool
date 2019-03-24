# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
from functools import update_wrapper
import re

from django.conf.urls import url
from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin.utils import unquote
from django.http import response
from django.template.response import SimpleTemplateResponse
from django.urls import resolve
from django.utils.text import capfirst

from .sites import CustomObjectToolAdminSiteMixin
from .utils import object_tool_context


class CustomObjectToolModelAdminMixin(object):
    """
    If you want to use custom object tool in your modeladmin,
    you should mix this class to your model admin
    """

    object_tools = []
    """object tools for both change list view and change view"""

    changelist_object_tools = []
    """object tools only for change list view"""

    change_object_tools = []
    """object tools only for change view"""

    @property
    def _base_change_list_template(self):
        parent = super(CustomObjectToolModelAdminMixin, self)
        return getattr(parent, "change_list_template", None)\
            or "admin/change_list.html"

    change_list_template = "admin/object_tool/baseview.html"

    @property
    def _base_change_form_template(self):
        parent = super(CustomObjectToolModelAdminMixin, self)
        return getattr(parent, "change_form_template", None)\
            or "admin/change_form.html"

    change_form_template = "admin/object_tool/baseview.html"

    def get_urls(self):
        urlpatterns = super(CustomObjectToolModelAdminMixin, self).get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        urlpatterns = [
            url(
                r"^objecttool/(.+)?$",
                wrap(self.object_tool_view),
                name="%s_%s_objecttool" % info
            )
        ] + urlpatterns
        return urlpatterns

    def _get_request_view(self, request):
        """util for get request view"""
        url_name = resolve(request.path_info).url_name
        match = re.search("_([^_]+?)$", url_name)
        view = match.group(1)
        if view == "objecttool":
            view = request.POST["object-tool-referrer-view"]
        return view

    def _get_base_object_tools(self, request):
        """
        Return the list of object tools
        """
        object_tools = []

        view = self._get_request_view(request)

        # Gather object tools from the admin site first
        if isinstance(self.admin_site, CustomObjectToolAdminSiteMixin):
            for (name, func) in self.admin_site.get_object_tools(view):
                description = getattr(
                    func, "short_description", name.replace("_", " "))
                object_tools.append((func, name, description))

        # Then gather them from the model admin and all parent classes
        for klass in self.__class__.mro()[::-1]:
            class_tools = list(getattr(klass, "object_tools", None) or [])
            class_tools.extend(getattr(
                klass, "{view}_object_tools".format(view=view), None) or [])
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
        func = None
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
                pass

        if func is None:
            raise ValueError("object tool {0} not found".format(object_tool))

        if hasattr(func, "short_description"):
            description = func.short_description
        else:
            description = capfirst(object_tool.replace("_", " "))
        return func, object_tool, description

    def response_object_tool(self, request, obj=None, extra_context=None):
        """
        Handle an admin object tool.
        """
        object_tools = self.get_object_tools(request)
        object_tool = object_tools[request.POST["object-tool"]]
        func = object_tool[0]
        rv = func(self, request, obj)
        if isinstance(rv, SimpleTemplateResponse):
            rv.context_data = rv.context_data or dict()
            rv.context_data.update(extra_context)
            return rv
        if isinstance(rv, response.HttpResponseBase):
            return rv
        else:
            redirect_url = request.POST["object-tool-referrer-url"]
            return response.HttpResponseRedirect(redirect_url)

    @csrf_protect_m
    def object_tool_view(self, request, object_id=None, extra_context=None):
        # handle object tool behaviors
        if "object-tool" not in request.POST:
            return response.HttpResponseBadRequest()

        name = request.POST["object-tool"]
        if name not in self.get_object_tools(request):
            return response.HttpResponseForbidden()

        object_tool = self.get_object_tool(name)
        allow_get = not getattr(object_tool, "allow_get", False)
        if not allow_get and request.method != "POST":
            return response.HttpResponseNotAllowed()

        obj = object_id and self.get_object(request, unquote(object_id))
        return self.response_object_tool(request, obj, extra_context)

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        extra_context = self._prepare_object_tool_view(request, extra_context)
        extra_context.update(
            object_tool_base_template=self._base_change_list_template
        )
        return super(CustomObjectToolModelAdminMixin, self).changelist_view(
            request, extra_context)

    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = self._prepare_object_tool_view(request, extra_context)
        extra_context.update(
            object_tool_base_template=self._base_change_form_template
        )
        return super(CustomObjectToolModelAdminMixin, self).changeform_view(
            request, object_id, form_url, extra_context)

    def _prepare_object_tool_view(self, request, extra_context=None):
        # update context
        extra_context = extra_context or {}
        extra_context.update(
            object_tools=tuple(map(
                lambda o: object_tool_context(*o),
                self.get_object_tools(request).values())),
            object_tool_referrer_url=request.get_full_path(),
            object_tool_referrer_view=self._get_request_view(request)
        )
        return extra_context


class CustomObjectToolModelAdmin(CustomObjectToolModelAdminMixin, ModelAdmin):
    pass
