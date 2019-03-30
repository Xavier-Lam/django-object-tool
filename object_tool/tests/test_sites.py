# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..sites import CustomObjectToolAdminSite
from .base import ObjectToolTestCase


class SiteTestCase(ObjectToolTestCase):
    def test_global_tools(self):
        def make_tool(funcname):
            def func():
                pass
            func.__name__ = str(funcname)
            return func

        global_tool = make_tool("global_tool")
        global_tool2 = make_tool("global_tool2")
        changeform_tool = make_tool("changeform_tool")
        changeform_tool2 = make_tool("changeform_tool2")
        changelist_tool = make_tool("changelist_tool")
        changelist_tool2 = make_tool("changelist_tool2")

        site = CustomObjectToolAdminSite()
        site.add_object_tool(global_tool)
        site.add_object_tool(global_tool2, name="global_tool_alias")
        site.add_object_tool(changelist_tool, view="changelist")
        site.add_object_tool(changelist_tool2, view="changelist", name="changelist_tool_alias")
        site.add_object_tool(changeform_tool, view="change")
        site.add_object_tool(changeform_tool2, view="change", name="changeform_tool_alias")

        global_tools = dict(
            global_tool=global_tool,
            global_tool_alias=global_tool2
        )

        tools = site.get_object_tools()
        self.assertEqual(global_tools, dict(tools))

        list_tools = global_tools.copy()
        list_tools.update(
            changelist_tool=changelist_tool,
            changelist_tool_alias=changelist_tool2
        )
        tools = site.get_object_tools("changelist")
        self.assertEqual(list_tools, dict(tools))

        form_tools = global_tools.copy()
        form_tools.update(
            changeform_tool=changeform_tool,
            changeform_tool_alias=changeform_tool2
        )
        tools = site.get_object_tools("change")
        self.assertEqual(form_tools, dict(tools))

        site.disable_object_tool("global_tool_alias")
        site.disable_object_tool("changelist_tool_alias", "changelist")
        site.disable_object_tool("changeform_tool_alias", "change")

        del global_tools["global_tool_alias"]
        del list_tools["global_tool_alias"]
        del list_tools["changelist_tool_alias"]
        del form_tools["global_tool_alias"]
        del form_tools["changeform_tool_alias"]

        tools = site.get_object_tools()
        self.assertEqual(global_tools, dict(tools))
        tools = site.get_object_tools("changelist")
        self.assertEqual(list_tools, dict(tools))
        tools = site.get_object_tools("change")
        self.assertEqual(form_tools, dict(tools))

        self.assertIs(site.get_object_tool("global_tool"), global_tool)
        self.assertIs(site.get_object_tool("global_tool_alias"), global_tool2)
        self.assertIs(site.get_object_tool("changelist_tool"), changelist_tool)
        self.assertIs(site.get_object_tool("changelist_tool_alias"), changelist_tool2)
        self.assertIs(site.get_object_tool("changeform_tool"), changeform_tool)
        self.assertIs(site.get_object_tool("changeform_tool_alias"), changeform_tool2)
