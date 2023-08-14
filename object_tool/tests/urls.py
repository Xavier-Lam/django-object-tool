# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.urls import re_path as url

urlpatterns = [
    url(r'^admin/', admin.site.urls)
]
