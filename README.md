# Django-object-tool

**django-object-tool** let you can customize django's object-tools bar. You can add actions to object-tools bar beside add-object button. The definition of object-tool action like django's default action.

![](docs/static/images/example.jpg?raw=true)

- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Write your first admin](#write-your-first-admin)
  - [Shortcut for hyperlink](#shortcut-for-hyperlink)
- [Compatibilities](#compatibilities)
  - [django-import-export](#django-import-export)
- [Example app](#example-app)
- [TODOS](#todos)
- [Change logs](#change-logs)
  - [0.0.1](#001)

## Quick Start
### Installation
Install django-object-tool by using pip

    pip install django-object-tool

then add it to your INSTALLED_APP

    # settings
    INSTALLED_APPS = (
        ...
        "object-tool"
    )

All prequisites are set up! See [Write your first admin](#Write-your-first-admin) to learn how to use django-object-tool in your project.

 > Note: We've patched django's default admin site(`django.contrib.admin.site`) by default, if you want to write your own admin site, please mix `object_tool.CustomObjectToolAdminSiteMixin` in your admin site class or direct inherit from `object_tool.CustomObjectToolAdminSite`.
 >
 > If you don't want to change the default site generate by django, you can set `OBJECT_TOOL_PATCHADMINSITE` to `False` in your settings file.

### Write your first admin
The object tool takes a request and an optional object, when this tool called inside a change view, the current editing object will be passed in.

    from object_tool import CustomObjectToolModelAdminMixin

    class SomeModelAdmin(CustomObjectToolModelAdminMixin, admin.ModelAdmin):
        object_tools = ("some_action",)

        def some_action(self, request, obj=None):
            if obj:
                obj.some_property = "value"
                obj.save()
            else:
                self.get_queryset(request).all().update(some_property="value")

### Shortcut for hyperlink
    from object_tool import CustomObjectToolModelAdminMixin, link_object_tool

    class SomeModelAdmin(CustomObjectToolModelAdminMixin, admin.ModelAdmin):
        object_tools = ("forkme", )

        forkme = link_object_tool(
            "https://github.com/Xavier-Lam/django-object-tool",
            "Fork me on github")



## Compatibilities
### django-import-export
We do not support [django-import-export](https://github.com/django-import-export/django-import-export/tree/master/import_export) yet, but we have plan support django-import-export in the future.

## Example app
We provided an example app

    git clone git@github.com:Xavier-Lam/django-object-tool.git
    cd django-object-tool/example
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

Then visit ***http://127.0.0.1:8000/admin*** and login as super admin by using account ***admin*** with password ***123456***.

## TODOS
* separate object tools definition in changelist view and change view
* patch for ModelAdmin
* unittests
* documentation
* shortcut for forms
* [django-import-export](https://github.com/django-import-export/django-import-export/tree/master/import_export) compatibility
* customize style for object tools

## Change logs
### 0.0.1
* custom object tools in changelist