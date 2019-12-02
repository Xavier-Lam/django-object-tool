# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.template.loaders.filesystem import Loader as FilesystemLoader
try:
    from functools import lru_cache
except ImportError:
    from django.utils.lru_cache import lru_cache


class Loader(FilesystemLoader):
    @lru_cache(maxsize=None)
    def get_dirs(self):
        from .. import BASE_DIR
        template_dir = os.path.join(BASE_DIR, "templates")
        return (template_dir, )
