# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models as m


class User(m.Model):
    name = m.CharField(max_length=32)
    handsome = m.BooleanField(default=False)

    def __str__(self):
        return self.name
