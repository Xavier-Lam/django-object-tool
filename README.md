# Django-object-tool

[![PyPI](https://img.shields.io/pypi/v/django-object-tool.svg)](https://pypi.org/project/django-object-tool)
[![Build Status](https://travis-ci.org/Xavier-Lam/django-object-tool.svg?branch=master)](https://travis-ci.org/Xavier-Lam/django-object-tool)

**django-object-tool** let you can customize django administration's object-tools bar. You can add actions to object-tools bar beside add-object button. The definition of object-tool action are almost same as django's default action.

> This is a pre alpha version without any unittest, there may have serveral problems and not compatible with some django or python versions.

![](docs/static/images/example.jpg?raw=true)

- [Django-object-tool](#django-object-tool)
  - [Quick Start](#quick-start)
    - [Installation](#installation)
    - [Write your first admin](#write-your-first-admin)
    - [Specific view only object tools](#specific-view-only-object-tools)
    - [Shortcuts](#shortcuts)
      - [Shortcut for hyperlinks](#shortcut-for-hyperlinks)
      - [Execute after confirmation](#execute-after-confirmation)
      - [Create a form](#create-a-form)
  - [Advanced usage](#advanced-usage)
    - [Site wide object tools](#site-wide-object-tools)
    - [Work with your own admin template](#work-with-your-own-admin-template)
    - [Ordering of object tools](#ordering-of-object-tools)
    - [Customize button styles](#customize-button-styles)
  - [Configurations](#configurations)
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
        "object-tool",
        "your app needs object-tool"
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

> The definition of object tool's action is almost same as django's default action, except the third parameter of the function is a optional current editing object rather than a queryset.

### Specific view only object tools
You can define a object tool only show in changelist view or change view by register it to changelist_object_tools or change_object_tools in your model admin.

    from object_tool import CustomObjectToolModelAdminMixin

    class SomeModelAdmin(CustomObjectToolModelAdminMixin, admin.ModelAdmin):
        changelist_object_tools = ("changelist_view_only_action",)
        change_object_tools = ("change_view_only_action", )

### Shortcuts
#### Shortcut for hyperlinks
You can create a hyperlink object tool like add-object by using `object_tool.link`, it takes a url as the first parameter and optional short_description as the second parameter.

    from object_tool import CustomObjectToolModelAdminMixin, link

    class SomeModelAdmin(CustomObjectToolModelAdminMixin, admin.ModelAdmin):
        object_tools = ("forkme", )

        forkme = link(
            "https://github.com/Xavier-Lam/django-object-tool",
            "Fork me on github")

#### Execute after confirmation
    @object_tool.confirm("are you sure to edit %(obj)s??", "confirm-tool")
    def confirm_action(self, request, obj=None):
        messages.success(request, "success!")

#### Create a form
With `object_tool.form` decorator, it is very easy to create a form view. This decorator takes a Form class as first parameter and it will auto render the form. When form is cleaned, it will actually execute decorated codes.

    from object_tool import CustomObjectToolModelAdminMixin, form

    class Form(forms.Form):
        text = forms.CharField()

    class UserAdmin(CustomObjectToolModelAdminMixin, admin.ModelAdmin):
        object_tools = ("greetings", )
        
        @form(Form, "greetings")
        def greetings(self, request, form, obj=None):
            text = form.cleaned_data["text"]
            tpl = "greetings to {name}: {text}"
            if obj:
                msg = tpl.format(name=obj.name, text=text)
            else:
                msg = tpl.format(name="all users", text=text)
            messages.info(request, msg)

## Advanced usage
### Site wide object tools
You can create a site wide object tool by register your object tool to the admin site which inherited from `object_tool.CustomObjectToolAdminSiteMixin`. You can set the second parameter of `object_tool.CustomObjectToolAdminSiteMixin.add_object_tool` to *changelist* or *change* if you want to make your object tool appear in changelist view or change view only.

    admin_site.add_object_tool(lambda modeladmin, request, obj=None: "some action")

> Note: Apparantly, you need to set your model admin's admin_site to the above site which your object tool registered to.

### Work with your own admin template
 In a `object_tool.CustomObjectToolAdminSiteMixin` class, rather than extends your template from `admin/change_list.html` or `admin/change_form.html`, you should extends `admin/object_tool/object-tool-items.html` instead.

* admin.py

        class SomeModelAdmin(CustomObjectToolModelAdminMixin, admin.ModelAdmin):
            change_list_template = "template.html"

* template.html

        {% extends 'admin/object_tool/baseview.html' %}

        ...your template code goes here...

### Ordering of object tools
Refer to the below table which lists the object tools' registration with the highest precedence at the top and lowest at the bottom.

| registration |
| --- |
| admin site global tools |
| admin site global specify view tools |
| tools defined in parent model admins |
| specify view tools defined in parent model admins |
| tools defined in current model admin |
| specify view tools defined in current model admin |

### Customize button styles
Assign *classes* property to object tool action can add classes to the object tool button.

    def some_action(self, request, obj=None):
        pass
    
    some_action.classes = "addlink"

## Configurations
| name | default | description |
| --- | --- | --- |
| OBJECT_TOOL_PATCHADMINSITE | True | replace `django.contrib.admin.sites.site` with `object_tool.CustomObjectToolAdminSite` when app loaded |
| OBJECT_TOOL_PATCHMODELADMIN | False | replace `django.contrib.admin.options.ModelAdmin` with `object_tool.CustomObjectToolModelAdmin` when app loaded |

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
* unittests
* [django-import-export](https://github.com/django-import-export/django-import-export/tree/master/import_export) compatibility

## Change logs
### 0.0.1
* custom object tools