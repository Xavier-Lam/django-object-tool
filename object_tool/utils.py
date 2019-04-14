# -*- coding: utf-8 -*-
from __future__ import unicode_literals

OBJECTTOOL_LINK_ALLOWED_PROPERTIES = ("href", "target")
OBJECTTOOL_ALLOWED_PROPERTIES = OBJECTTOOL_LINK_ALLOWED_PROPERTIES + (
    "__name__", "allow_get", "classes", "help_text", "short_description")


def object_tool_context(func, name, short_description):
    context = {
        property: getattr(func, property)
        for property in dir(func)
        if property in OBJECTTOOL_ALLOWED_PROPERTIES
    }
    context["short_description"] = short_description
    return (name, context)
