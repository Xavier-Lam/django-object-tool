# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

from .sites import patch_admin


class ObjectToolConfig(AppConfig):
    name = "object_tool"

    def ready(self):
        patch_admin()
