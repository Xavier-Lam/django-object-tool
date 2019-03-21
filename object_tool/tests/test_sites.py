# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..sites import CustomObjectToolAdminSite
from .base import ObjectToolTestCase


class SiteTestCase(ObjectToolTestCase):
    def test_register_tool(self):
        site = CustomObjectToolAdminSite()
        site.add_object_tool("global_tool")
        self.add_object_tool("global_tool2", name="global_tool_alias")
        site.add_object_tool("change_tool")
        self.add_object_tool("change_tool2", name="change_tool_alias")
        site.add_object_tool("changelist_tool")
        self.add_object_tool("changelist_tool2", name="changelist_tool_alias")

        tools = site.get_object_tools()
        self.assertEqual(set("global_tool", "global_tool_alias"), tools)
