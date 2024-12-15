# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import unicode_literals

__title__ = "django-object-tool"
__description__ = "Django admin customize object tools support"
__url__ = "https://github.com/Xavier-Lam/django-object-tool"
__version__ = "0.0.12"
__author__ = "Xavier-Lam"
__author_email__ = "Lam.Xavier@hotmail.com"

default_app_config = 'object_tool.apps.ObjectToolConfig'


import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


from .admin import CustomObjectToolModelAdmin, CustomObjectToolModelAdminMixin
from .apps import ObjectToolConfig
from .shortcuts import confirm, form, link
from .sites import (
    CustomObjectToolAdminSite, CustomObjectToolAdminSiteMixin, patch_admin)

# shortnames
ObjectToolModelAdmin = CustomObjectToolModelAdmin
ObjectToolModelAdminMixin = CustomObjectToolModelAdminMixin
ObjectToolAdminSite = CustomObjectToolAdminSite
ObjectToolAdminSiteMixin = CustomObjectToolAdminSiteMixin
