# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
import object_tool
from object_tool import CustomObjectToolModelAdminMixin

from .models import User


class Form(forms.Form):
    text = forms.CharField(required=True)


class UserAdmin(CustomObjectToolModelAdminMixin, admin.ModelAdmin):
    object_tools = ("make_handsome", "greetings", "confirm_action")
    changelist_object_tools = ("forkme", )

    list_display = ("name", "handsome")
    search_fields = ("name",)

    forkme = object_tool.link(
        "https://github.com/Xavier-Lam/django-object-tool",
        "Fork me on github", classes="viewsitelink", target="_blank")

    @object_tool.form(Form, "greetings")
    def greetings(self, request, form, obj=None):
        text = form.cleaned_data["text"]
        tpl = "greetings to {name}: {text}"
        if obj:
            msg = tpl.format(name=obj.name, text=text)
        else:
            msg = tpl.format(name="all users", text=text)
        messages.info(request, msg)

    @object_tool.confirm("are you sure to edit %(obj)s??", "confirm-tool")
    def confirm_action(self, request, obj=None):
        messages.success(request, "success!")

    def make_handsome(self, request, obj=None):
        if obj:
            obj.handsome = True
            obj.save()
        else:
            self.get_queryset(request).all().update(handsome=True)
        messages.success(request, "success!")
    make_handsome.help_text = _("change handsome property to True")

admin.site.register(User, UserAdmin)
