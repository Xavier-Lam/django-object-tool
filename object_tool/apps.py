# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.apps import AppConfig
from django.conf import settings
from django.template.engine import Engine

from .sites import patch_admin


class ObjectToolConfig(AppConfig):
    name = "object_tool"

    def ready(self):
        patch_admin()

    @classmethod
    def register(cls, ready=False):
        """register object-tool without add to INSTALLED_APPS"""
        from . import BASE_DIR

        # add template loader to default engine
        template_engine = Engine.get_default()
        loader = "object_tool.template.loaders.Loader"
        if loader not in template_engine.loaders:
            template_engine.loaders = list(template_engine.loaders) + [loader]

        # add static dir to settings
        static_dir = os.path.join(BASE_DIR, "static")
        static_dirs = list(settings.STATICFILES_DIRS)
        if static_dir not in static_dirs:
            static_dirs.append(static_dir)
        settings.STATICFILES_DIRS = static_dirs

        ready and cls.ready(None)

