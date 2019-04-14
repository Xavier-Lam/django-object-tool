# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import wraps

from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from .utils import object_tool_context, OBJECTTOOL_ALLOWED_PROPERTIES


def link(url, short_description, **kwargs):
    """
    A short cut for superlink object tool

        class DebugAdmin(CustomObjectToolModelAdminMixin, ModelAdmin):
            object_tools = ["forkme"]

            forkme = link(
                "https://github.com/Xavier-Lam/django-object-tool", _("fork"))
    """
    def wrapper(modeladmin, request, obj=None):
        return HttpResponseRedirect(url)

    kwargs["short_description"] = short_description
    kwargs["allow_get"] = True
    kwargs["href"] = url
    for key, value in kwargs.items():
        if key in OBJECTTOOL_ALLOWED_PROPERTIES:
            setattr(wrapper, key, value)

    return wrapper


def form(form_class, short_description="", template=None, confirm_field="confirm", **kwargs):
    """
    A short cut for generate form view

        from object_tool import CustomObjectToolModelAdminMixin, form

        class Form(forms.Form):
            text = forms.CharField()

        class UserAdmin(CustomObjectToolModelAdminMixin, admin.ModelAdmin):
            object_tools = ("text", )

            @form(Form, "text")
            def text(self, request, form, obj=None):
                pass
    """
    return _confirm_view(
        form_class=form_class, short_description=short_description,
        template=template, confirm_field=confirm_field, **kwargs)


def confirm(text=None, short_description="", template=None, confirm_field="confirm", **kwargs):
    """
    A shortcut for confirm page

        @confirm("are you sure to edit %(obj)s??", "confirm-tool")
        def confirm_action(self, request, obj=None):
            pass
    """
    text = text or _("Are you sure?")
    return _confirm_view(
        confirm_text=text, short_description=short_description,
        template=template, confirm_field=confirm_field, **kwargs)


def _confirm_view(form_class=None, short_description="", template=None, confirm_text="", confirm_field="confirm", **kwargs):
    def decorator(func):
        name = kwargs.pop("__name__", None) or func.__name__
        title = short_description or name

        @wraps(func)
        def wrapper(modeladmin, request, obj=None):
            form = None

            if request.method == "POST" and request.POST.get(confirm_field):
                form = form_class and form_class(request.POST)
                if not form or form.is_valid():
                    return func(modeladmin, request, form, obj) if form\
                        else func(modeladmin, request, obj)
            else:
                form = form_class and form_class()

            context = dict(
                modeladmin.admin_site.each_context(request),
                action=name,
                opts=modeladmin.model._meta,
                confirm_text=confirm_text % dict(obj=obj or ""),
                form=form,
                title=title,
                obj=obj,
                object_id=obj and obj.pk,
                object_tool=object_tool_context(
                    func, name, title)
            )

            template_ = template or\
                getattr(modeladmin, "objecttool_form_template", None) or\
                "admin/object_tool/form.html"

            return TemplateResponse(request, template_, context)

        kwargs["short_description"] = title
        kwargs["allow_get"] = True
        for key, value in kwargs.items():
            if key in OBJECTTOOL_ALLOWED_PROPERTIES:
                setattr(wrapper, key, value)

        return wrapper

    return decorator
