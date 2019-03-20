# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.conf import settings


class ObjectToolConfig(AppConfig):
    name = 'object_tool'

    def ready(self):
        if getattr(settings, "OBJECT_TOOL_PATCHADMINSITE", True):
            # replace default admin with object tool admin
            from django.contrib import admin
            from .sites import site
            site._registry.update(admin.site._registry)
            setattr(admin.sites, "site", site)
            setattr(admin, "site", site)
